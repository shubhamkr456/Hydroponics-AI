function SensorCard({ title, value, unit, icon }) {
  return (
    <div className="sensor-card">

      <div className="sensor-header">
        <h2>
          <span className="sensor-icon">{icon}</span>
          {title}
        </h2>
      </div>

      <div className="sensor-body">
        <h1>
          {value} {unit}
        </h1>
      </div>

    </div>
  );
}

export default SensorCard;