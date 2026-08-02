from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import paho.mqtt.client as mqtt

from database.db import db
from database.models import SensorReading
from config import DATABASE_URI

# ==========================================
# Flask App
# ==========================================

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

CORS(app)

# ==========================================
# MQTT Configuration
# ==========================================

MQTT_BROKER = "192.168.0.101"       # Raspberry Pi IP
MQTT_PORT = 1883
MQTT_TOPIC_CONTROL = "hydroponics/control"

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

# ==========================================
# In-Memory Storage
# ==========================================

latest_data = {
    "temperature": 28.4,
    "humidity": 65,
    "ph": 6.20,
    "tds": 350,
    "light_percentage": 72,
    "reservoir_distance_cm": 18,
    "lastUpdate": "--:--"
}

sensor_history = []

# ==========================================
# Routes
# ==========================================

@app.route("/")
def home():
    return jsonify({
        "project": "Hydroponics AI",
        "status": "Running"
    })


@app.route("/captures", methods=["POST"])
def captures():

    global latest_data, sensor_history

    try:

        data = request.get_json()

        # ----------------------------
        # Update live dashboard
        # ----------------------------

        latest_data = data

        sensor_history.append(data)

        if len(sensor_history) > 100:
            sensor_history.pop(0)

        # ----------------------------
        # Save to PostgreSQL
        # ----------------------------

        reading = SensorReading(

            temperature=data.get("temperature"),

            humidity=data.get("humidity"),

            ph=data.get("ph"),

            tds=data.get("tds"),

            light_percentage=data.get("light_percentage"),

            reservoir_distance_cm=data.get("reservoir_distance_cm")

        )

        db.session.add(reading)

        db.session.commit()

        print("\n========== Sensor Data ==========")
        print(data)

        return jsonify({
            "status": "success"
        }), 200

    except Exception as e:

        db.session.rollback()

        print("Capture Error:", e)

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/api/latest", methods=["GET"])
def latest():

    return jsonify(latest_data)


@app.route("/api/history", methods=["GET"])
def history():

    return jsonify(sensor_history)


@app.route("/api/relay", methods=["POST"])
def relay():

    try:

        data = request.get_json()

        print("\n========== Relay Command ==========")
        print(data)

        result = mqtt_client.publish(
            MQTT_TOPIC_CONTROL,
            json.dumps(data)
        )

        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print("✅ MQTT Command Published")
        else:
            print("❌ MQTT Publish Failed")

        return jsonify({
            "status": "success",
            "message": "Relay command sent"
        }), 200

    except Exception as e:

        print("Relay Error:", e)

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================
# Run Flask
# ==========================================

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )