import "./ToggleSwitch.css";

function ToggleSwitch({ label, isOn, onToggle }) {
  return (
    <div className="toggle-card">
      <div className="toggle-label">
        {label}
      </div>

      <div
        className={`toggle-switch ${isOn ? "on" : ""}`}
        onClick={onToggle}
      >
        <div className="toggle-knob"></div>
      </div>
    </div>
  );
}

export default ToggleSwitch;