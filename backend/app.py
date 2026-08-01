from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Stores the most recent sensor reading
latest_data = {
    "temperature": 28.4,
    "humidity": 65,
    "ph": 6.20,          # Placeholder until pH sensor is available
    "tds": 350,
    "light": 72,
    "reservoir": 18,
    "lastUpdate": "--:--"
}

# Stores the sensor history in an array
sensor_history = []


@app.route("/")
def home():
    return {
        "project": "Hydroponics AI",
        "status": "Running"
    }

@app.route("/captures", methods=["POST"])
def captures():
    global latest_data, sensor_history

    latest_data = request.get_json()

    sensor_history.append(latest_data)

    # Keep only the last 100 readings
    if len(sensor_history) > 100:
        sensor_history.pop(0)

    print(latest_data)

    return jsonify({"status": "success"}), 200

@app.route("/api/latest", methods=["GET"])
def latest():
    return jsonify(latest_data)


@app.route("/api/history", methods=["GET"])
def history():
    return jsonify(sensor_history)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)