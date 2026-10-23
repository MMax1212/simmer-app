import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/auth";
export function Home() {
    const { user } = useAuth();
    const notice = (useLocation().state as {
        notice?: string;
    } | null)?.notice;
    return <section className="hero">
    {notice && <p role="alert" className="error">{notice}</p>}
    <h1>{user ? "Welcome back, " + user.username : "Welcome to Simmer"}</h1>
    <p className="muted">{user ? "You are signed in." : "Create an account or log in to get started."}</p>
    {!user && <div className="row">
      <Link to="/register" className="button">Create an account</Link>
      <Link to="/login" className="button secondary">Log in</Link>
    </div>}
    {user?.role === "admin" && <Link to="/admin" className="button">Manage users</Link>}
  </section>;
}
