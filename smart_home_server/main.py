from flask import Flask, request, jsonify
import RPi.GPIO as GPIO
import time
from threading import Thread

# Настройка GPIO
DEVICE_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(DEVICE_PIN, GPIO.OUT)

# Создание приложения Flask
app = Flask(__name__)

# Функция управления устройством
def control_device(state):
    GPIO.output(DEVICE_PIN, GPIO.HIGH if state else GPIO.LOW)

# Таймер
def timer_action(duration, state):
    time.sleep(duration)
    control_device(state)

@app.route('/device', methods=['POST'])
def manage_device():
    data = request.json
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
