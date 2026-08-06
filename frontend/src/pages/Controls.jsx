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

            </main>

        </>

    );

}

export default Controls;