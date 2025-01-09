from flask import Flask, request, jsonify
import time
from threading import Thread

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

# Настройка GPIO (будет работать с мок-объектом)
DEVICE_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(DEVICE_PIN, GPIO.OUT)

# Создание приложения Flask
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1 MB

# Функция управления устройством
def control_device(state):
    GPIO.output(DEVICE_PIN, GPIO.HIGH if state else GPIO.LOW)

# Таймер
def timer_action(duration, state):
    time.sleep(duration)
    control_device(state)

@app.route('/device', methods=['POST'])
def manage_device():
    # Проверяем длину тела запроса
    content_length = request.content_length
    if content_length is None or content_length > 1 * 1024 * 1024:  # 1 MB
        return jsonify({"error": "Request body is too large"}), 413

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

    if action == "on":
        control_device(True)
        return jsonify({"status": "Device turned ON"})
    elif action == "off":
        control_device(False)
        return jsonify({"status": "Device turned OFF"})
    elif action == "timer":
        try:
            duration = int(data.get('duration', 0))
            if duration < 0:
                return jsonify({"error": "Duration must be a positive integer"}), 400
            state = bool(data.get('state', False))
        except ValueError:
            return jsonify({"error": "Invalid data type for duration or state"}), 400

        Thread(target=timer_action, args=(duration, state)).start()
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
