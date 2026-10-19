import { Link } from "react-router-dom";
import { useAuth } from "../context/auth";

export function Home() {
  const { user } = useAuth();
  return (
    <section className="hero">
      <h1>{user ? `Welcome back, ${user.username}` : "Cook, share, and simmer together."}</h1>
      <p className="muted">Save your favorite recipes and build your culinary identity.</p>
      <div className="row">
        {user ? (
          <>
            <Link to="/recipes/new" className="button">Add a recipe</Link>
            <Link to="/recipes/mine" className="button secondary">My Recipes</Link>
          </>
        ) : (
          <>
            <Link to="/register" className="button">Create an account</Link>
            <Link to="/login" className="button secondary">Log in</Link>
          </>
        )}
      </div>
    </section>
  );
}
