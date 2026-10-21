import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ErrorMessage } from "../components/ErrorMessage";
import { useAuth } from "../context/auth";
import { api, errorText, type Recipe } from "../services/api";

export function RecipeDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setRecipe(null);
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
              <li key={i.id}>{[i.amount, i.unit, i.name].filter((x) => x != null && x !== "").join(" ")}</li>
            ))}
          </ul>
        </>
      )}
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
