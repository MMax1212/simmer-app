import { useEffect, useState, type FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ErrorMessage } from "../components/ErrorMessage";
import { api, errorText, type Ingredient, type RecipeInput } from "../services/api";

const EMPTY: RecipeInput = {
  title: "", description: "", instructions: "",
  prep_time_mins: null, cook_time_mins: null, servings: null,
  ingredients: [{ name: "", quantity: null, unit: "" }],
};

const toNum = (v: string) => (v === "" ? null : Number(v));

/** US1.4: used for both /recipes/new and /recipes/:id/edit */
export function RecipeForm() {
  const { id } = useParams();
  const editing = id !== undefined;
  const navigate = useNavigate();
  const [recipe, setRecipe] = useState<RecipeInput>(EMPTY);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!editing) return;
    api.getRecipe(Number(id))
      .then((r) => setRecipe({ ...r, ingredients: r.ingredients.length ? r.ingredients : EMPTY.ingredients }))
      .catch((e) => setError(errorText(e)));
  }, [editing, id]);

  const set = <K extends keyof RecipeInput>(k: K, v: RecipeInput[K]) => setRecipe({ ...recipe, [k]: v });
  const setIng = (i: number, changes: Partial<Ingredient>) =>
    set("ingredients", recipe.ingredients.map((ing, j) => (j === i ? { ...ing, ...changes } : ing)));

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    const body: RecipeInput = {
      ...recipe,
      description: recipe.description || null,
      // Drop blank ingredient rows; send empty units as null.
      ingredients: recipe.ingredients
        .filter((i) => i.name.trim())
        .map(({ name, quantity, unit }) => ({ name: name.trim(), quantity, unit: unit || null })),
    };
    try {
      const saved = editing ? await api.updateRecipe(Number(id), body) : await api.createRecipe(body);
      navigate(`/recipes/${saved.id}`);
    } catch (err) {
      setError(errorText(err));
      setBusy(false);
    }
  }

  return (
    <form className="card" onSubmit={onSubmit}>
      <h1>{editing ? "Edit recipe" : "New recipe"}</h1>
      <label>Title<input value={recipe.title} onChange={(e) => set("title", e.target.value)} required maxLength={120} /></label>
      <label>Description<textarea value={recipe.description ?? ""} onChange={(e) => set("description", e.target.value)} rows={2} /></label>

      <div className="grid-3">
        <label>Prep (min)<input type="number" min={0} value={recipe.prep_time_mins ?? ""} onChange={(e) => set("prep_time_mins", toNum(e.target.value))} /></label>
        <label>Cook (min)<input type="number" min={0} value={recipe.cook_time_mins ?? ""} onChange={(e) => set("cook_time_mins", toNum(e.target.value))} /></label>
        <label>Servings<input type="number" min={1} value={recipe.servings ?? ""} onChange={(e) => set("servings", toNum(e.target.value))} /></label>
      </div>

      <fieldset>
        <legend>Ingredients</legend>
        {recipe.ingredients.map((ing, i) => (
          <div className="ingredient-row" key={i}>
            <input aria-label="Quantity" type="number" min={0} step="any" placeholder="Qty" value={ing.quantity ?? ""} onChange={(e) => setIng(i, { quantity: toNum(e.target.value) })} />
            <input aria-label="Unit" placeholder="Unit" value={ing.unit ?? ""} onChange={(e) => setIng(i, { unit: e.target.value })} />
            <input aria-label="Ingredient" placeholder="Ingredient" value={ing.name} onChange={(e) => setIng(i, { name: e.target.value })} />
            <button type="button" className="secondary" aria-label="Remove ingredient" onClick={() => set("ingredients", recipe.ingredients.filter((_, j) => j !== i))}>×</button>
          </div>
        ))}
        <button type="button" className="secondary" onClick={() => set("ingredients", [...recipe.ingredients, { name: "", quantity: null, unit: "" }])}>
          + Add ingredient
        </button>
      </fieldset>

      <label>Instructions<textarea value={recipe.instructions} onChange={(e) => set("instructions", e.target.value)} required rows={8} placeholder={"1. Preheat oven…\n2. …"} /></label>
      <ErrorMessage error={error} />
      <div className="row">
        <button type="submit" disabled={busy}>{busy ? "Saving…" : "Save recipe"}</button>
        <button type="button" className="secondary" onClick={() => navigate(-1)}>Cancel</button>
      </div>
    </form>
  );
}
