import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { BookOpen } from "lucide-react";
import { ErrorMessage } from "../components/ErrorMessage";
import { api, errorText, type Recipe } from "../services/api";

const PAGE_SIZE = 20;

// --- US1.5: Personal Recipe Tab (Personal Recipe Library Dashboard) ---
export function MyRecipes() {
  const [recipes, setRecipes] = useState<Recipe[] | null>(null);
  const [offset, setOffset] = useState(0);
  const [error, setError] = useState<string | null>(null);

  // --- US1.5: Task 5.2 & 5.3: Fetch and Paginate User-Specific Saved Recipes ---
  useEffect(() => {
    let active = true;
    setRecipes(null);
    setError(null);
    api.myRecipes(offset, PAGE_SIZE + 1).then((items) => { if (active) setRecipes(items); })
      .catch((e) => { if (active) setError(errorText(e)); });
    return () => { active = false; };
  }, [offset]);

  if (error) return <ErrorMessage error={error} />;
  if (!recipes) return <p className="muted">Loading…</p>;

  return <section>
    <div className="row space-between"><h1>My Recipes</h1><Link to="/recipes/new" className="button">+ New recipe</Link></div>
    {recipes.length === 0 ? (
      <div className="flex flex-col items-center gap-4 py-10">
        <BookOpen size={64} aria-hidden="true" />
        <p className="muted">No recipes yet. <Link to="/recipes/new">Add your first one.</Link></p>
      </div>
    ) : <div className="recipe-grid">{recipes.slice(0, PAGE_SIZE).map((recipe) => (
      <Link to={"/recipes/" + recipe.id} key={recipe.id} className="recipe-card">
        <h3>{recipe.title}</h3>{recipe.description && <p className="muted clamp">{recipe.description}</p>}
        <p className="small">{recipe.prep_time_mins + recipe.cook_time_mins} min · serves {recipe.servings}</p>
      </Link>
    ))}</div>}
    {(offset > 0 || recipes.length > PAGE_SIZE) && <nav className="row mt-4" aria-label="Recipe pages">
      <button disabled={offset === 0} onClick={() => setOffset(offset - PAGE_SIZE)}>Previous</button>
      <span>Page {offset / PAGE_SIZE + 1}</span>
      <button disabled={recipes.length <= PAGE_SIZE} onClick={() => setOffset(offset + PAGE_SIZE)}>Next</button>
    </nav>}
  </section>;
}
