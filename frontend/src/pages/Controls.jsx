import { useState } from "react";

import Sidebar from "../components/Sidebar";
import ToggleSwitch from "../components/ToggleSwitch";

function Controls() {

    const [switches, setSwitches] = useState({
        pumpA: false,
        pumpB: false,
        pumpC: false,
        waterPump: false
    });
    const [incubatorMode, setIncubatorMode] = useState("AUTO");

    const [growLight, setGrowLight] = useState(false);

async function toggleControl(name, relay) {

    const newState = !switches[name];

    try {

        const response = await fetch(
            "http://127.0.0.1:5000/api/relay",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    device_id: "esp32_main",
                    relay: relay,
                    state: newState
                })
            }
        );

        if (response.ok) {

            setSwitches(prev => ({
                ...prev,
                [name]: newState
            }));

            // Auto-reset the UI after 5 seconds
            if (newState) {

                setTimeout(() => {

                    setSwitches(prev => ({
                        ...prev,
                        [name]: false
                    }));

                }, 5000);

            }

        }

    } catch (err) {

        console.error(err);

    }

}
async function sendIncubatorCommand(payload) {

    try {

        const response = await fetch(
            "http://127.0.0.1:5000/api/relay",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    device_id: "esp32_incubator",
                    ...payload
                })
            }
        );

        if (!response.ok) {
            throw new Error("Failed to send command");
        }

    } catch (err) {

        console.error(err);

    }
}
async function setMode(mode) {

    setIncubatorMode(mode);

    await sendIncubatorCommand({
        mode: mode
    });

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

            <main className="dashboard">

                <h1>Controls</h1>

                <h2>Hydroponics Controller</h2>

                <ToggleSwitch
                    label="Nutrient Pump A"
                    isOn={switches.pumpA}
                    onToggle={() => toggleControl("pumpA", 33)}
                />

                <ToggleSwitch
                    label="Nutrient Pump B"
                    isOn={switches.pumpB}
                    onToggle={() => toggleControl("pumpB", 25)}
                />

                <ToggleSwitch
                    label="Nutrient Pump C"
                    isOn={switches.pumpC}
                    onToggle={() => toggleControl("pumpC", 26)}
                />

                <ToggleSwitch
                    label="Water Circulation Pump"
                    isOn={switches.waterPump}
                    onToggle={() => toggleControl("waterPump", 4)}
                />
                <hr />

                <h2>Incubator Controller</h2>

                <div style={{ marginBottom: "20px" }}>

                    <button
                        onClick={() => setMode("AUTO")}
                        disabled={incubatorMode === "AUTO"}
                    >
                        AUTO
                    </button>

                    <button
                        onClick={() => setMode("MANUAL")}
                        disabled={incubatorMode === "MANUAL"}
                        style={{ marginLeft: "10px" }}
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