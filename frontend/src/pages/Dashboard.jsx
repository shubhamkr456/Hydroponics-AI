import { useState, useEffect } from "react";
import Navbar from "../components/Navbar";
import SensorCard from "../components/SensorCard";
import api from "../services/api";
import Sidebar from "../components/Sidebar";


function Dashboard() {
 // all sensor data sits here
 const [sensorData, setSensorData] = useState({
  temperature: 0,
  humidity: 0,
  tds: 0,
  ph: 0,
  light_percentage: 0,
  reservoir_distance_cm: 0,
  lastUpdate: "--:--",
});

  useEffect(() => {

    const fetchData = async () => {

        try {

            const response = await api.get("/api/latest");

            setSensorData(response.data);

        } catch (error) {

            console.error(error);

        }

    };

    fetchData();

    const timer = setInterval(fetchData, 5000);

    return () => clearInterval(timer);

}, []);
  



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
    icon="🧫 "
    title="pH"
    value={sensorData.ph}
    unit=""
  />

  <SensorCard
    icon="☀ "
    title="Light"
    value={sensorData.light_percentage}
    unit="%"
  />

  <SensorCard
    icon="🛢 "
    title="Reservoir"
    value={sensorData.reservoir_distance_cm}
    unit="cm"
  />

</div>
      </main>
    </>
  );
}

export default Dashboard;