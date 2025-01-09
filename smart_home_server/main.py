from flask import Flask, request, jsonify
import time
from threading import Thread, Event, Lock


# Мок-объект GPIO (замените на RPi.GPIO для реального устройства)
class MockGPIO:
    BCM = "BCM"
    OUT = "OUT"
    HIGH = 1
    LOW = 0

    def setmode(self, mode):
        print(f"GPIO mode set to {mode}")

    def setup(self, pin, mode):
        print(f"GPIO pin {pin} set to {mode}")

    def output(self, pin, state):
        print(f"GPIO pin {pin} set to {'HIGH' if state == self.HIGH else 'LOW'}")


# Заменяем оригинальный RPi.GPIO на мок
GPIO = MockGPIO()

# Настройка GPIO
DEVICE_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(DEVICE_PIN, GPIO.OUT)

# Создание приложения Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 128  # 128 B
limiter = Limiter(get_remote_address, app=app, default_limits=["10 per minute"])

# Ограничения
MAX_TIMER_DURATION = 3600  # 1 час в секундах
current_timer_thread = None
cancel_event = Event()
timer_lock = Lock()


# Функция управления устройством
def control_device(state):
    GPIO.output(DEVICE_PIN, GPIO.HIGH if state else GPIO.LOW)


# Таймер
def timer_action(duration, state):
    global cancel_event
    try:
        start_time = time.time()
        while time.time() - start_time < duration:
            if cancel_event.is_set():
                return  # Прерываем таймер
            time.sleep(0.1)  # Короткий сон для проверки отмены
        control_device(state)
    except Exception as e:
        app.logger.error(f"Timer action failed: {e}")


@app.route('/device', methods=['POST'])
@limiter.limit("5 per minute")  # Локальный лимит
def manage_device():
    global current_timer_thread, cancel_event

    # Проверяем длину тела запроса
    if request.content_length is None or request.content_length > 128:
        return jsonify({"error": "Request body is too large"}), 413

    # Проверяем JSON
    try:
        data = request.json
    except Exception as e:
        app.logger.error(f"Invalid JSON received: {e}")
        return jsonify({"error": "Invalid JSON"}), 400

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    action = data.get('action')
    if action not in {"on", "off", "timer"}:
        return jsonify({"error": "Invalid action"}), 400

    app.logger.info(f"Action received: {action}")

    # Управляем состоянием устройства
    if action in {"on", "off"}:
        with timer_lock:
            # Прерываем текущий таймер, если он запущен
            if current_timer_thread and current_timer_thread.is_alive():
                cancel_event.set()  # Сигнал остановки таймера
                current_timer_thread.join(timeout=5)  # Ждем завершения потока

        # Выполняем команду включения или выключения
        control_device(action == "on")
        return jsonify({"status": f"Device turned {'ON' if action == 'on' else 'OFF'}"})

    elif action == "timer":
        try:
            duration = int(data.get('duration', 0))
            if duration <= 0 or duration > MAX_TIMER_DURATION:
                return jsonify({"error": f"Duration must be between 1 and {MAX_TIMER_DURATION} seconds"}), 400
            state = data.get('state')
            if not isinstance(state, bool):
                return jsonify({"error": "State must be a boolean"}), 400
        except ValueError:
            return jsonify({"error": "Invalid data type for duration or state"}), 400

        # Прерываем текущий таймер, если он запущен
        with timer_lock:
            if current_timer_thread and current_timer_thread.is_alive():
                cancel_event.set()  # Сигнал остановки таймера
                current_timer_thread.join(timeout=5)  # Ждем завершения потока

            # Сбрасываем флаг отмены и запускаем новый таймер
            cancel_event.clear()
            current_timer_thread = Thread(target=timer_action, args=(duration, state))
            current_timer_thread.start()

        return jsonify({"status": f"Timer set for {duration} seconds"})


@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "Request body is too large"}), 413


@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unexpected error: {e}")
    return jsonify({"error": "An unexpected error occurred"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
