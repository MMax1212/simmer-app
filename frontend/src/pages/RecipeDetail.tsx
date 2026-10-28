import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ErrorMessage } from "../components/ErrorMessage";
import { useAuth } from "../context/auth";
import { api, errorText, type Recipe } from "../services/api";

// --- US1.5: Personal Recipe Tab (Recipe Detail Display & Author Actions) ---
export function RecipeDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [checked, setChecked] = useState<number[]>([]);
  const [error, setError] = useState<string | null>(null);

  // --- US1.5: Task 5.4: Fetch Recipe Detail from Backend ---
  useEffect(() => {
    let active = true;
    setRecipe(null);
    setChecked([]);
    setError(null);
    api.getRecipe(Number(id)).then((value) => { if (active) setRecipe(value); })
      .catch((e) => { if (active) setError(errorText(e)); });
    return () => { active = false; };
  }, [id]);

  if (error) return <ErrorMessage error={error} />;
  if (!recipe) return <p className="muted">Loading…</p>;

  const canEdit = user && (user.id === recipe.author_id || user.role === "admin");

  async function onDelete() {
    if (!recipe || !confirm(`Delete "${recipe.title}"?`)) return;
    try {
      await api.deleteRecipe(recipe.id);
      navigate("/recipes/my-recipes");
    } catch (e) {
      setError(errorText(e));
    }
  }

  return (
    <article className="card">
      <h1>{recipe.title}</h1>
      <p className="muted">by {recipe.author_username}</p>
      {recipe.image_url && <img src={recipe.image_url} alt={recipe.title} className="max-h-80 w-full rounded-lg object-cover" />}
      <p className="muted">{[recipe.cuisine, recipe.meal_type, recipe.difficulty].filter(Boolean).join(" · ")}</p>
      {recipe.description && <p>{recipe.description}</p>}
      <ul className="meta">
        {recipe.prep_time_mins != null && <li>Prep {recipe.prep_time_mins} min</li>}
        {recipe.cook_time_mins != null && <li>Cook {recipe.cook_time_mins} min</li>}
        {recipe.servings != null && <li>Serves {recipe.servings}</li>}
      </ul>
      {recipe.ingredients.length > 0 && (
        <>
          <h2>Ingredients</h2>
          <ul>
            {recipe.ingredients.map((i) => (
              <li key={i.id}><label className="ingredient-check"><input type="checkbox" checked={checked.includes(i.id!)} onChange={(event) => setChecked((current) => event.target.checked ? [...current, i.id!] : current.filter((id) => id !== i.id))} /><span style={{ textDecoration: checked.includes(i.id!) ? "line-through" : "none" }}>{[i.amount, i.unit, i.name].filter((x) => x != null && x !== "").join(" ")}</span></label></li>
            ))}
          </ul>
        </>
      )}
      <details><summary>Required kitchen tools</summary>
        {recipe.tools?.length ? <ul>{recipe.tools.map((tool) => <li key={tool}>{tool}</li>)}</ul> : <p className="muted">No special tools listed.</p>}
      </details>
      <h2>Instructions</h2>
      <ol className="list-decimal pl-6 space-y-3">{recipe.steps.map((step) => <li key={step.id} className="instructions">{step.instruction}</li>)}</ol>
      {canEdit && (
        <div className="row">
          <Link to={`/recipes/${recipe.id}/edit`} className="button">Edit</Link>
          <button className="danger" onClick={onDelete}>Delete</button>
        </div>
      )}
    </article>
  );
}
