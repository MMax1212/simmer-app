import { useEffect, useRef, useState } from "react";
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
  // Cooking progress is local UI state, not a change to the saved recipe.
  const [checked, setChecked] = useState<number[]>([]);
  const [error, setError] = useState<string | null>(null);

  // --- US2.3 Task 2.3.3: "I Cooked This!" Modal State ---
  const [showLogModal, setShowLogModal] = useState(false);
  const [notes, setNotes] = useState("");
  const [rating, setRating] = useState<number | null>(null);
  const [logError, setLogError] = useState<string | null>(null);
  const [logSuccess, setLogSuccess] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const isSubmittingRef = useRef(false);

  // --- US1.5: Task 5.4: Fetch Recipe Detail from Backend ---
  useEffect(() => {
    let active = true;
    setRecipe(null);
    // Ingredient IDs and progress belong to the recipe currently being viewed.
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

  // --- US2.3 Task 2.3.3: Submit Cooking Log Action ---
  async function onSaveCookingLog() {
    if (isSubmittingRef.current || !recipe) return;
    isSubmittingRef.current = true;
    setIsSubmitting(true);
    setLogError(null);

    const body: { notes?: string; rating?: number } = {};
    if (notes.trim()) body.notes = notes.trim();
    if (rating !== null) body.rating = rating;

    try {
      await api.completeRecipe(recipe.id, body);
      setShowLogModal(false);
      setLogSuccess(true);
    } catch (e) {
      setLogError(errorText(e));
    } finally {
      isSubmittingRef.current = false;
      setIsSubmitting(false);
    }
  }

  function onCancelLog() {
    setShowLogModal(false);
    setLogError(null);
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

      {logSuccess && (
        <p role="status" className="success">
          Saved to cooking history
        </p>
      )}

      {user && (
        <div className="row" style={{ marginTop: "1rem" }}>
          <button
            type="button"
            className="button secondary"
            onClick={() => {
              setShowLogModal(true);
              setLogError(null);
            }}
          >
            I Cooked This
          </button>
          {canEdit && (
            <>
              <Link to={`/recipes/${recipe.id}/edit`} className="button">Edit</Link>
              <button className="danger" onClick={onDelete}>Delete</button>
            </>
          )}
        </div>
      )}

      {showLogModal && (
        <div role="dialog" aria-label="I Cooked This" className="modal-backdrop">
          <div className="card modal-content">
            <h2>I Cooked This</h2>
            {logError && <p role="alert" className="error">{logError}</p>}
            <form onSubmit={(e) => { e.preventDefault(); onSaveCookingLog(); }}>
              <label htmlFor="notes">
                Notes
              </label>
              <textarea
                id="notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="How did it turn out? Any modifications?"
                rows={3}
              />
              <fieldset>
                <legend>Rating</legend>
                <div className="star-rating">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <label key={star}>
                      <input
                        type="radio"
                        name="rating"
                        value={star}
                        checked={rating === star}
                        onChange={() => setRating(star)}
                        aria-label={`${star} star${star > 1 ? "s" : ""}`}
                      />
                      {star} star{star > 1 ? "s" : ""}
                    </label>
                  ))}
                </div>
              </fieldset>
              <div className="row">
                <button
                  type="submit"
                  disabled={isSubmitting}
                >
                  Save cooking log
                </button>
                <button
                  type="button"
                  className="secondary"
                  onClick={onCancelLog}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </article>
  );
}
