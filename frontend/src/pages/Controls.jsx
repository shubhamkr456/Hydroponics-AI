import { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import ToggleSwitch from "../components/ToggleSwitch";

// Import your dedicated stylesheet
import "./Controls.css";

function Controls() {
    const [switches, setSwitches] = useState({
        pumpA: false,
        pumpB: false,
        pumpC: false,
        waterPump: false
    });
    
    const [incubatorMode, setIncubatorMode] = useState("AUTO");
    const [growLight, setGrowLight] = useState(false);
    
    // Tracks the Low Water Mode manual override
    const [lowWaterMode, setLowWaterMode] = useState(false);

    // Actively poll the Flask backend to sync UI with the hardware's true state
    useEffect(() => {
        const syncHardwareState = async () => {
            try {
                const response = await fetch("http://127.0.0.1:5000/api/sensors/latest"); 
                if (response.ok) {
                    const data = await response.json();
                    
                    // If the ESP32 safety watchdog turned the pump off, update the toggle instantly
                    if (data.low_water_override !== undefined) {
                        setLowWaterMode(data.low_water_override);
                    }
                }
            } catch (err) {
                // Fails silently to prevent console spam if backend is momentarily unreachable
            }
        };

        // Check hardware state every 2 seconds
        const intervalId = setInterval(syncHardwareState, 2000);
        return () => clearInterval(intervalId);
    }, []);

    async function toggleControl(name, relay) {
        const newState = !switches[name];
        try {
            const response = await fetch("http://127.0.0.1:5000/api/relay", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    device_id: "esp32_main",
                    relay: relay,
                    state: newState
                })
            });

            if (response.ok) {
                setSwitches(prev => ({ ...prev, [name]: newState }));

                // 10-second auto-reset (matches ESP32 PUMP_RUNTIME exactly)
                if (newState) {
                    setTimeout(() => {
                        setSwitches(prev => ({ ...prev, [name]: false }));
                    }, 10000); 
                }
            }
        } catch (err) {
            console.error(err);
        }
    }

    async function toggleLowWaterMode() {
        const newState = !lowWaterMode;
        try {
            const response = await fetch("http://127.0.0.1:5000/api/relay", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    device_id: "esp32_main",
                    low_water_override: newState
                })
            });

            if (response.ok) {
                setLowWaterMode(newState);
            }
        } catch (err) {
            console.error(err);
        }
    }

    async function sendIncubatorCommand(payload) {
        try {
            const response = await fetch("http://127.0.0.1:5000/api/relay", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    device_id: "esp32_incubator",
                    ...payload
                })
            });
            if (!response.ok) {
                throw new Error("Failed to send command");
            }
        } catch (err) {
            console.error(err);
        }
    }

    async function setMode(mode) {
        setIncubatorMode(mode);
        await sendIncubatorCommand({ mode: mode });
    }

    async function toggleGrowLight() {
        const newState = !growLight;
        setGrowLight(newState);
        await sendIncubatorCommand({
            mode: "MANUAL",
            light: newState
        });
    }

    return (
        <>
            <Sidebar />
            <main className="dashboard" style={{ padding: "2rem", maxWidth: "900px", margin: "0 auto" }}>
                <h1 style={{ fontSize: "2.5rem", margin: 0, color: "#0f172a" }}>Controls</h1>

                <h2 className="minimal-header">Hydroponics Tower</h2>
                


                {/* Enlarged Main Pump */}
                <div className="main-pump-wrapper">
                    <ToggleSwitch
                        label="Main Reservoir Pump"
                        isOn={switches.waterPump}
                        onToggle={() => toggleControl("waterPump", 4)}
                    />
                </div>

                <ToggleSwitch
                    label="Reservoir Low Water Mode"
                    isOn={lowWaterMode}
                    onToggle={toggleLowWaterMode}
                />

                {/* Nutrient Pumps Reordered & Wrapped in Red Box */}
                <div className="nutrient-pump-wrapper">
                    <ToggleSwitch
                        label="Nutrient Pump A"
                        isOn={switches.pumpC}
                        onToggle={() => toggleControl("pumpC", 26)}
                    />
                    <ToggleSwitch
                        label="Nutrient Pump B"
                        isOn={switches.pumpB}
                        onToggle={() => toggleControl("pumpB", 25)}
                    />
                    <ToggleSwitch
                        label="Nutrient Pump C"
                        isOn={switches.pumpA}
                        onToggle={() => toggleControl("pumpA", 33)}
                    />
                </div>
                
                <h2 className="minimal-header">Incubator Hub</h2>
                
                <div className="mode-container">
                    <button
                        className="mode-btn"
                        onClick={() => setMode("AUTO")}
                        disabled={incubatorMode === "AUTO"}
                    >
                        AUTO
                    </button>
                    <button
                        className="mode-btn"
                        onClick={() => setMode("MANUAL")}
                        disabled={incubatorMode === "MANUAL"}
                    >
                        MANUAL
                    </button>
                </div>

                <ToggleSwitch
                    label="Grow Light"
                    isOn={growLight}
                    onToggle={() => {
                        if (incubatorMode === "MANUAL") {
                            toggleGrowLight();
                        }
                    }}
                />
            </main>
        </>
    );
}

export default Controls;