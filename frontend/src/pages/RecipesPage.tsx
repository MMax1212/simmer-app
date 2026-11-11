import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ErrorMessage } from "../components/ErrorMessage";
import { api, errorText, type RecipeSummary } from "../services/api";

const CATEGORIES = ["All", "Italian", "Mexican", "Asian", "American", "Mediterranean", "other"];

export function RecipesPage() {
  const [query, setQuery] = useState("");
  const [selectedCuisine, setSelectedCuisine] = useState<string | null>(null);
  const [recipes, setRecipes] = useState<RecipeSummary[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // US2.2 (Task 2.2): 300ms Debounce & live search dispatch
  useEffect(() => {
    let active = true;
    setLoading(true);

    const timer = setTimeout(() => {
      api.searchRecipes({
        q: query,
        cuisine: selectedCuisine ?? undefined,
      })
        .then((res) => {
          if (active) {
            setRecipes(res.items);
            setLoading(false);
          }
        })
        .catch((e) => {
          if (active) {
            setError(errorText(e));
            setLoading(false);
          }
        });
    }, 300); // 300ms debounce

    return () => {
      active = false;
      clearTimeout(timer); // Cancel timer if user types another letter within 300ms
    };
  }, [query, selectedCuisine]);

  // Handler to clear search and category filters
  const handleResetFilters = () => {
    setQuery("");
    setSelectedCuisine(null);
  };

  return (
    <section>
      <h1>Explore Recipes</h1>
      <p className="muted" style={{ marginBottom: "1rem" }}>
        Discover recipes by title, ingredients, or cuisine.
      </p>

      {/* Search Input */}
      <div style={{ marginBottom: "1rem" }}>
        <input
          type="search"
          placeholder="Search recipes by title or ingredient..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>

      {/* Category Filter Pills (Task 2.3) */}
      <div className="chips" style={{ marginBottom: "1.5rem" }} role="group" aria-label="Category filters">
        {CATEGORIES.map((cat) => {
          const isActive = (cat === "All" && selectedCuisine === null) || selectedCuisine === cat;
          return (
            <button
              type="button"
              key={cat}
              className={`chip ${isActive ? "on" : ""}`}
              onClick={() => setSelectedCuisine(cat === "All" ? null : cat)}
            >
              {cat}
            </button>
          );
        })}
      </div>

      {error && <ErrorMessage error={error} />}
      {loading && !recipes && <p className="muted">Loading recipes…</p>}

      {/* Empty State (Task 2.4) */}
      {!loading && recipes && recipes.length === 0 && (
        <div className="card" style={{ textAlign: "center", padding: "2.5rem 1rem" }}>
          <p style={{ fontWeight: 600, fontSize: "1.1rem", marginBottom: "0.5rem" }}>
            No recipes match your search criteria.
          </p>
          <p className="muted" style={{ marginBottom: "1.2rem" }}>
            Try adjusting your search keywords or resetting filters.
          </p>
          <div>
            <button type="button" onClick={handleResetFilters}>
              Reset all filters
            </button>
          </div>
        </div>
      )}

      {/* Search Results Grid */}
      {recipes && recipes.length > 0 && (
        <div className="recipe-grid">
          {recipes.map((recipe) => (
            <Link to={"/recipes/" + recipe.id} key={recipe.id} className="recipe-card">
              <h3>{recipe.title}</h3>
              {recipe.cuisine && <span className="small muted">Cuisine: {recipe.cuisine}</span>}
              <p className="small muted">
                By {recipe.author_username} · {recipe.cook_time_mins} min · {recipe.difficulty}
              </p>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}