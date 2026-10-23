import { useEffect, useState, type FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ErrorMessage } from "../components/ErrorMessage";
import { api, errorText, type Ingredient, type RecipeInput } from "../services/api";

const emptyRecipe = (): RecipeInput => ({
  title: "", description: "", cuisine: "", meal_type: "", difficulty: "medium", image_url: "",
  prep_time_mins: 0, cook_time_mins: 0, servings: 1,
  ingredients: [{ name: "", amount: null, unit: "" }],
  steps: [{ step_number: 1, instruction: "" }],
});

// --- US1.4: Recipe Creation & Saving (Recipe Authoring & Editing Form) ---
export function RecipeForm() {
  const { id } = useParams();
  const editing = id !== undefined;
  const navigate = useNavigate();
  const [recipe, setRecipe] = useState<RecipeInput>(emptyRecipe);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(editing);

  useEffect(() => {
    let active = true;
    setRecipe(emptyRecipe());
    setError(null);
    setLoading(editing);
    setBusy(false);
    if (editing) {
      api.getRecipe(Number(id)).then((r) => {
        if (active) setRecipe({
          title: r.title, description: r.description, cuisine: r.cuisine, meal_type: r.meal_type,
          difficulty: r.difficulty, image_url: r.image_url, prep_time_mins: r.prep_time_mins,
          cook_time_mins: r.cook_time_mins, servings: r.servings,
          ingredients: r.ingredients.length ? r.ingredients : emptyRecipe().ingredients,
          steps: r.steps.length ? r.steps : emptyRecipe().steps,
        });
      }).catch((e) => { if (active) setError(errorText(e)); })
        .finally(() => { if (active) setLoading(false); });
    }
    return () => { active = false; };
  }, [editing, id]);

  const set = <K extends keyof RecipeInput>(key: K, value: RecipeInput[K]) =>
    setRecipe((current) => ({ ...current, [key]: value }));
  const setIngredient = (index: number, changes: Partial<Ingredient>) =>
    setRecipe((current) => ({ ...current, ingredients: current.ingredients.map((item, i) => i === index ? { ...item, ...changes } : item) }));

  // --- US1.4: Task 4.4 & 4.5: Validate Recipe Inputs and Persist to Backend ---
  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!recipe.ingredients.length || !recipe.steps.length) {
      setError("Add at least one ingredient and one step.");
      return;
    }
    if (recipe.title.trim().length < 3 || recipe.ingredients.some((i) => !i.name.trim() || !i.unit?.trim() || !(Number(i.amount) > 0)) ||
        recipe.steps.some((step) => step.instruction.trim().length < 3)) {
      setError("Enter a title, complete ingredients with positive amounts, and instructions of at least 3 characters.");
      return;
    }
    setBusy(true);
    setError(null);
    const body: RecipeInput = {
      ...recipe, title: recipe.title.trim(), description: recipe.description || null,
      cuisine: recipe.cuisine || null, meal_type: recipe.meal_type || null, image_url: recipe.image_url || null,
      ingredients: recipe.ingredients.map(({ name, amount, unit }) => ({ name: name.trim(), amount, unit: unit!.trim() })),
      steps: recipe.steps.map((step, index) => ({ step_number: index + 1, instruction: step.instruction.trim() })),
    };
    try {
      const saved = editing ? await api.updateRecipe(Number(id), body) : await api.createRecipe(body);
      navigate("/recipes/" + saved.id);
    } catch (err) { setError(errorText(err)); setBusy(false); }
  }

  if (loading) return <p className="muted">Loading recipe…</p>;

  return (
    <form className="card" onSubmit={onSubmit}>
      <h1>{editing ? "Edit recipe" : "New recipe"}</h1>
      <label>Title<input value={recipe.title} onChange={(e) => set("title", e.target.value)} required minLength={3} maxLength={150} /></label>
      <label>Description<textarea value={recipe.description ?? ""} onChange={(e) => set("description", e.target.value)} maxLength={2000} rows={2} /></label>
      <div className="grid-3">
        <label>Cuisine<input value={recipe.cuisine ?? ""} onChange={(e) => set("cuisine", e.target.value)} maxLength={50} /></label>
        <label>Meal type<input value={recipe.meal_type ?? ""} onChange={(e) => set("meal_type", e.target.value)} maxLength={50} /></label>
        <label>Difficulty<select value={recipe.difficulty} onChange={(e) => set("difficulty", e.target.value as RecipeInput["difficulty"])}>
          <option value="easy">Easy</option><option value="medium">Medium</option><option value="hard">Hard</option>
        </select></label>
      </div>
      <label>Recipe image URL<input type="url" value={recipe.image_url ?? ""} onChange={(e) => set("image_url", e.target.value)} maxLength={255} pattern="https?://.*" /></label>
      <div className="grid-3">
        <label>Prep (min)<input type="number" min={0} max={10000} value={recipe.prep_time_mins} onChange={(e) => set("prep_time_mins", Number(e.target.value))} required /></label>
        <label>Cook (min)<input type="number" min={0} max={10000} value={recipe.cook_time_mins} onChange={(e) => set("cook_time_mins", Number(e.target.value))} required /></label>
        <label>Servings<input type="number" min={1} max={100} value={recipe.servings} onChange={(e) => set("servings", Number(e.target.value))} required /></label>
      </div>
      <fieldset>
        <legend>Ingredients</legend>
        {recipe.ingredients.map((ingredient, index) => (
          <div className="ingredient-row" key={index}>
            <input aria-label={"Amount " + (index + 1)} type="number" min={0} step="any" placeholder="Amount" required value={ingredient.amount ?? ""} onChange={(e) => setIngredient(index, { amount: e.target.value === "" ? null : Number(e.target.value) })} />
            <input aria-label={"Unit " + (index + 1)} placeholder="Unit" required maxLength={30} value={ingredient.unit ?? ""} onChange={(e) => setIngredient(index, { unit: e.target.value })} />
            <input aria-label={"Ingredient " + (index + 1)} placeholder="Ingredient" required maxLength={100} value={ingredient.name} onChange={(e) => setIngredient(index, { name: e.target.value })} />
            <button type="button" className="secondary" aria-label={"Remove ingredient " + (index + 1)} onClick={() => set("ingredients", recipe.ingredients.filter((_, i) => i !== index))}>×</button>
          </div>
        ))}
        <button type="button" className="secondary" onClick={() => set("ingredients", [...recipe.ingredients, { name: "", amount: null, unit: "" }])}>+ Add ingredient</button>
      </fieldset>
      <fieldset>
        <legend>Instructions</legend>
        {recipe.steps.map((step, index) => (
          <div className="flex items-start gap-2" key={index}>
            <label className="flex-1">Step {index + 1}<textarea value={step.instruction} required minLength={3} maxLength={10000} rows={3} onChange={(e) => set("steps", recipe.steps.map((s, i) => i === index ? { ...s, instruction: e.target.value } : s))} /></label>
            <button type="button" className="secondary" aria-label={"Remove step " + (index + 1)} onClick={() => set("steps", recipe.steps.filter((_, i) => i !== index))}>×</button>
          </div>
        ))}
        <button type="button" className="secondary" onClick={() => set("steps", [...recipe.steps, { step_number: recipe.steps.length + 1, instruction: "" }])}>+ Add step</button>
      </fieldset>
      <ErrorMessage error={error} />
      <div className="row">
        <button type="submit" disabled={busy}>{busy ? "Saving…" : "Save recipe"}</button>
        <button type="button" className="secondary" onClick={() => navigate(-1)}>Cancel</button>
      </div>
    </form>
  );
}
