import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ErrorMessage } from "../components/ErrorMessage";
import { api, errorText, type Recipe } from "../services/api";

/** US1.5: grid of recipes the logged-in user created. */
export function MyRecipes() {
  const [recipes, setRecipes] = useState<Recipe[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.myRecipes().then(setRecipes).catch((e) => setError(errorText(e)));
  }, []);

  if (error) return <ErrorMessage error={error} />;
  if (!recipes) return <p className="muted">Loading…</p>;

  return (
    <section>
      <div className="row space-between">
        <h1>My Recipes</h1>
        <Link to="/recipes/new" className="button">+ New recipe</Link>
      </div>
      {recipes.length === 0 ? (
        <p className="muted">No recipes yet. <Link to="/recipes/new">Add your first one.</Link></p>
      ) : (
        <div className="recipe-grid">
          {recipes.map((r) => {
            const total = (r.prep_time_mins ?? 0) + (r.cook_time_mins ?? 0);
            return (
              <Link to={`/recipes/${r.id}`} key={r.id} className="recipe-card">
                <h3>{r.title}</h3>
                {r.description && <p className="muted clamp">{r.description}</p>}
                <p className="small">{total > 0 ? `${total} min` : ""}{r.servings ? ` · serves ${r.servings}` : ""}</p>
              </Link>
            );
          })}
        </div>
      )}
    </section>
  );
}
