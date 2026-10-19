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
            <NavLink to="/recipes/mine">My Recipes</NavLink>
            <NavLink to="/recipes/new">New Recipe</NavLink>
            <NavLink to="/profile">Profile</NavLink>
            {user.role === "admin" && <NavLink to="/admin">Admin</NavLink>}
            <button className="link-button" onClick={() => { logout(); navigate("/"); }}>
              Log out
            </button>
          </>
        ) : (
          <>
            <NavLink to="/login">Log in</NavLink>
            <NavLink to="/register" className="button">Sign up</NavLink>
          </>
        )}
      </nav>
    </header>
  );
}
