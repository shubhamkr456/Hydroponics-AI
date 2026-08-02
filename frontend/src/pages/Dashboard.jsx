import { useState, useEffect } from "react";

import Sidebar from "../components/Sidebar";
import SensorCard from "../components/SensorCard";
import ToggleSwitch from "../components/ToggleSwitch";

import api from "../services/api";

function Dashboard() {

  // ==========================================
  // Sensor Data
  // ==========================================

  const [sensorData, setSensorData] = useState({
    temperature: 0,
    humidity: 0,
    tds: 0,
    ph: 0,
    light_percentage: 0,
    reservoir_distance_cm: 0,
    lastUpdate: "--:--",
  });

  // ==========================================
  // Pump States
  // ==========================================

const [pumpState, setPumpState] = useState({
  33: false,
  25: false,
  26: false,
  4: false,
});
const pumps = [
  {
    gpio: 33,
    name: "Nutrient C",
    icon: "🧪",
  },
  {
    gpio: 25,
    name: "Nutrient B",
    icon: "🧪",
  },
  {
    gpio: 26,
    name: "Nutrient A",
    icon: "🧪",
  },
  {
    gpio: 4,
    name: "Water Pump",
    icon: "💧",
  },
];
  // ==========================================
  // Fetch Live Sensor Data
  // ==========================================

  useEffect(() => {

    const fetchData = async () => {

      try {

        const response = await api.get("/api/latest");

        setSensorData(response.data);

      } catch (error) {

        console.error("Failed to fetch sensor data:", error);

      }

    };

    fetchData();

    const timer = setInterval(fetchData, 5000);

    return () => clearInterval(timer);

  }, []);

  // ==========================================
  // Pump Control
  // ==========================================

  const togglePump = async (relay) => {

  try {

    setPumpState(prev => ({
      ...prev,
      [relay]: true,
    }));

    await api.post("/api/relay", {
      relay,
      state: true,
    });

    setTimeout(() => {

      setPumpState(prev => ({
        ...prev,
        [relay]: false,
      }));

    }, 5000);

  } catch (error) {

    console.error(error);

    setPumpState(prev => ({
      ...prev,
      [relay]: false,
    }));

  }

  };
  // ==========================================
  // Dashboard
  // ==========================================

  return (

    <>
      <Sidebar />

      <main className="dashboard">

        <h2>Live Sensor Monitoring</h2>

        <div className="sensor-grid">

          <SensorCard
            icon="🌡"
            title="Temperature"
            value={sensorData.temperature}
            unit="°C"
          />

          <SensorCard
            icon="💧"
            title="Humidity"
            value={sensorData.humidity}
            unit="%"
          />

          <SensorCard
            icon="🧪"
            title="TDS"
            value={sensorData.tds}
            unit="ppm"
          />

          <SensorCard
            icon="🧫"
            title="pH"
            value={sensorData.ph}
            unit=""
          />

          <SensorCard
            icon="☀"
            title="Light"
            value={sensorData.light_percentage}
            unit="%"
          />

          <SensorCard
            icon="🛢"
            title="Reservoir"
            value={sensorData.reservoir_distance_cm}
            unit="cm"
          />

        </div>

        <h2>Pump Control</h2>

        <div className="sensor-grid">

          {pumps.map((pump) => (

            <ToggleSwitch
              key={pump.gpio}
              label={`${pump.icon} ${pump.name} `}
              isOn={pumpState[pump.gpio]}
              onToggle={() => togglePump(pump.gpio)}
            />

          ))}

        </div>

      </main>
    </>

  );
}

export default Dashboard;