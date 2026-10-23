import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/auth";

export function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="navbar">
      <Link to="/" className="brand">Simmer</Link>
      <nav>
        {user ? (
          <>
            {/* US1.3: User Profile Navigation */}
            <NavLink to="/profile">Profile</NavLink>
            {/* US1.2: Admin Console Navigation */}
            {user.role === "admin" && <NavLink to="/admin">Admin</NavLink>}
            {/* US1.1: User Logout */}
            <button className="link-button" onClick={() => { logout(); navigate("/"); }}>
              Log out
            </button>
          </>
        ) : (
          <>
            {/* US1.1: User Login & Registration Navigation */}
            <NavLink to="/login">Log in</NavLink>
            <NavLink to="/register" className="button">Sign up</NavLink>
          </>
        )}
      </nav>
    </header>
  );
}
