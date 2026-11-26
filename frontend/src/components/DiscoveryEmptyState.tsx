import { Link } from "react-router-dom";

/** Empty success states should offer a next step instead of suggesting a failed request. */
export function DiscoveryEmptyState({ message }: { message: string }) {
  return (
    <div className="card">
      <p>{message}</p>
      <p className="muted">Explore the collection or share something you love to cook.</p>
      <div className="row">
        <Link to="/recipes" className="button secondary">Browse all recipes</Link>
        {/* The existing protected route takes signed-out readers through login. */}
        <Link to="/recipes/new" className="button">Share a recipe</Link>
      </div>
    </div>
  );
}
