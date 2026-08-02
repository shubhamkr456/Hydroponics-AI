from datetime import datetime

from database.db import db


class SensorReading(db.Model):

    __tablename__ = "sensor_readings"

    id = db.Column(db.Integer, primary_key=True)

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)

    ph = db.Column(db.Float)
    tds = db.Column(db.Float)

    light_percentage = db.Column(db.Float)

    reservoir_distance_cm = db.Column(db.Float)

    def __repr__(self):

        return f"<SensorReading {self.id}>"