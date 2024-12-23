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
    if content_length > 1 * 1024 * 1024:  # 1 MB
        return jsonify({"error": "Request body is too large"}), 413

    data = request.json
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    action = data.get('action')  # "on", "off" или "timer"
    if action == "on":
        control_device(True)
        return jsonify({"status": "Device turned ON"})
    elif action == "off":
        control_device(False)
        return jsonify({"status": "Device turned OFF"})
    elif action == "timer":
        duration = data.get('duration', 0)  # В секундах
        state = data.get('state', False)  # True для ON, False для OFF
        Thread(target=timer_action, args=(duration, state)).start()
        return jsonify({"status": f"Timer set for {duration} seconds"})
    else:
        return jsonify({"error": "Invalid action"}), 400

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "Request body is too large"}), 413

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
