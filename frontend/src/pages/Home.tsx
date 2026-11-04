import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/auth";
import { api, errorText, type RecipeSummary } from "../services/api";
import { ErrorMessage } from "../components/ErrorMessage";
import { BookOpen } from "lucide-react";

// Filter pills configuration
const FILTER_PRESETS = [
  { label: "All", type: "all", value: "" },
  { label: "Italian", type: "cuisine", value: "Italian" },
  { label: "Mexican", type: "cuisine", value: "Mexican" },
  { label: "Asian", type: "cuisine", value: "Asian" },
  { label: "Breakfast", type: "meal_type", value: "breakfast" },
  { label: "Dinner", type: "meal_type", value: "dinner" },
  { label: "#quick", type: "tag", value: "quick" },
  { label: "#healthy", type: "tag", value: "healthy" },
];

export function Home() {
  const { user } = useAuth();
  const notice = (useLocation().state as { notice?: string } | null)?.notice;
  const [activeFilter, setActiveFilter] = useState({ type: "all", value: "" });
  const [recipes, setRecipes] = useState<RecipeSummary[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // Fetch recipes whenever the selected filter changes
  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    const filterParam =
      activeFilter.type === "cuisine"
        ? { cuisine: activeFilter.value }
        : activeFilter.type === "meal_type"
        ? { meal_type: activeFilter.value }
        : activeFilter.type === "tag"
        ? { tag: activeFilter.value }
        : {};
    api
      .searchRecipes(filterParam)
      .then((res) => {
        if (active) setRecipes(res.items);
      })
      .catch((e) => {
        if (active) setError(errorText(e));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [activeFilter]);
  return (
    <div className="flex flex-col gap-6">
      {/* Hero Banner */}
      <section className="hero">
        {notice && <p role="alert" className="error">{notice}</p>}
        <h1>{user ? `Welcome back, ${user.username}` : "Cook, share, and simmer together."}</h1>
        <p className="muted">Discover delicious recipes or share your culinary creations.</p>
        <div className="row">
          {user ? (
            <>
              <Link to="/recipes/new" className="button">Add a recipe</Link>
              <Link to="/recipes/my-recipes" className="button secondary">My Recipes</Link>
            </>
          ) : (
            <>
              <Link to="/register" className="button">Create an account</Link>
              <Link to="/login" className="button secondary">Log in</Link>
            </>
          )}
        </div>
      </section>
      {/* --- US2.1 (Task 2.1.4): Category Filter Pills Bar --- */}
      <section className="card">
        <div className="flex flex-col gap-2">
          <label className="text-sm font-semibold">Filter by Category & Tags:</label>
          <div className="chips" role="group" aria-label="Category and tag filter">
            {FILTER_PRESETS.map((preset) => {
              const isSelected =
                activeFilter.type === preset.type &&
                activeFilter.value.toLowerCase() === preset.value.toLowerCase();
              return (
                <button
                  key={preset.label}
                  type="button"
                  className={`chip ${isSelected ? "on" : ""}`}
                  onClick={() =>
                    setActiveFilter(
                      isSelected && preset.type !== "all"
                        ? { type: "all", value: "" }
                        : { type: preset.type, value: preset.value }
                    )
                  }
                >
                  {preset.label}
                  {isSelected && preset.type !== "all" && <span className="ml-1 font-bold">×</span>}
                </button>
              );
            })}
          </div>
        </div>
      </section>
      {/* Recipe Discovery Grid */}
      <section style={{ minHeight: "280px" }}>
        {error && <ErrorMessage error={error} />}
        {loading && recipes === null && <p className="muted">Loading recipes…</p>}

        {recipes && recipes.length === 0 && (
          <div
            className="flex flex-col items-center gap-3 py-12 text-center card"
            style={{ opacity: loading ? 0.6 : 1, transition: "opacity 0.15s ease" }}
          >
            <BookOpen size={48} className="text-stone-400" />
            <h3 className="text-lg font-semibold">No recipes found</h3>
            <p className="muted">No recipes match the selected category filter.</p>
            {activeFilter.type !== "all" && (
              <button
                type="button"
                className="secondary small mt-2"
                onClick={() => setActiveFilter({ type: "all", value: "" })}
              >
                Reset Filter
              </button>
            )}
          </div>
        )}

        {recipes && recipes.length > 0 && (
          <div
            className="recipe-grid"
            style={{
              opacity: loading ? 0.6 : 1,
              transition: "opacity 0.15s ease",
            }}
          >
            {recipes.map((r) => (
              <Link to={`/recipes/${r.id}`} key={r.id} className="recipe-card">
                <h3>{r.title}</h3>
                <div className="row text-xs gap-1.5 my-1">
                  {r.cuisine && <span className="chip text-xs py-0.5 px-2">{r.cuisine}</span>}
                  {r.meal_type && <span className="chip text-xs py-0.5 px-2">{r.meal_type}</span>}
                  <span className="muted">· {r.difficulty}</span>
                </div>
                {r.tags && r.tags.length > 0 && (
                  <div className="row gap-1 my-1">
                    {r.tags.map((t) => (
                      <span key={t} className="chip on text-xs py-0.5 px-2 font-semibold">
                        {t}
                      </span>
                    ))}
                  </div>
                )}
                <p className="small muted">
                  By {r.author_username} · {r.cook_time_mins} min cook
                </p>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}