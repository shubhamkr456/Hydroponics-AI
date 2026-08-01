import "./Navbar.css";

function Navbar() {
  return (
    <nav className="navbar">

      <div className="navbar-left">
        🌱 <span>Hydroponics AI</span>
      </div>

      <div className="navbar-right">

        <div className="status">
          <span className="status-dot"></span>
          Online
        </div>

        <div className="user">
          Shubham
        </div>

      </div>

    </nav>
  );
}

export default Navbar;