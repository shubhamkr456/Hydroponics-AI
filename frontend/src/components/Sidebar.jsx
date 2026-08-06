import "./Sidebar.css";
import { NavLink } from "react-router-dom";

function Sidebar() {
    return (
        <aside className="sidebar">

            <h2>🌱 Hydro AI</h2>

            <ul>

                <li>
                    <NavLink
                        to="/"
                        className={({ isActive }) =>
                            isActive ? "active-link" : ""
                        }
                    >
                        🏠 Dashboard
                    </NavLink>
                </li>

                <li>
                    <NavLink
                        to="/controls"
                        className={({ isActive }) =>
                            isActive ? "active-link" : ""
                        }
                    >
                        🎛 Controls
                    </NavLink>
                </li>

                <li>
                    <NavLink
                        to="/analytics"
                        className={({ isActive }) =>
                            isActive ? "active-link" : ""
                        }
                    >
                        📊 Analytics
                    </NavLink>
                </li>

                <li>
                    <NavLink
                        to="/cameras"
                        className={({ isActive }) =>
                            isActive ? "active-link" : ""
                        }
                    >
                        📷 Cameras
                    </NavLink>
                </li>

                <li>
                    <NavLink
                        to="/settings"
                        className={({ isActive }) =>
                            isActive ? "active-link" : ""
                        }
                    >
                        ⚙ Settings
                    </NavLink>
                </li>

            </ul>

        </aside>
    );
}

export default Sidebar;