import { BrowserRouter, Routes, Route } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Controls from "./pages/Controls";

function App() {

    return (

        <BrowserRouter>

            <Routes>

                <Route
                    path="/"
                    element={<Dashboard />}
                />

                <Route
                    path="/controls"
                    element={<Controls />}
                />

            </Routes>

        </BrowserRouter>

    );

}

export default App;