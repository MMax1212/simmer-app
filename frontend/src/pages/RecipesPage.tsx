import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { SlidersHorizontal } from "lucide-react";
import { DietaryFilterDrawer } from "../components/DietaryFilterDrawer";
import { ErrorMessage } from "../components/ErrorMessage";
import { RecipeCard } from "../components/RecipeCard";
import { api, errorText, type RecipeSummary } from "../services/api";

const CATEGORIES = ["All", "Italian", "Mexican", "Asian", "American", "Mediterranean", "other"];

export function RecipesPage() {
  const [searchParams] = useSearchParams();

  const [query, setQuery] = useState(() => searchParams.get("q") || "");
  const [selectedCuisine, setSelectedCuisine] = useState<string | null>(
    () => searchParams.get("cuisine") || null
  );
  const [selectedDietary, setSelectedDietary] = useState<string[]>(() => {
    const d = searchParams.get("dietary");
    return d ? d.split(",").map((s) => (s.startsWith("#") ? s : `#${s.trim()}`)) : [];
  });
  const [selectedOccasion, setSelectedOccasion] = useState<string | null>(() => {
    const o = searchParams.get("occasion");
    return o ? (o.startsWith("#") ? o : `#${o.trim()}`) : null;
  });
  const [selectedMaxTime, setSelectedMaxTime] = useState<number | null>(() => {
    const m = searchParams.get("max_time");
    return m ? Number(m) : null;
  });
  const [isFilterDrawerOpen, setIsFilterDrawerOpen] = useState(false);
  const [recipes, setRecipes] = useState<RecipeSummary[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // US2.2 & US4.4: 300ms Debounce & live multi-facet search dispatch
  useEffect(() => {
    let active = true;
    setLoading(true);

    const timer = setTimeout(() => {
      const dietaryParam =
        selectedDietary.length > 0
          ? selectedDietary.map((t) => t.replace(/^#/, "")).join(",")
          : undefined;
      const occasionParam = selectedOccasion ? selectedOccasion.replace(/^#/, "") : undefined;

      api.searchRecipes({
        q: query,
        cuisine: selectedCuisine ?? undefined,
        dietary: dietaryParam,
        occasion: occasionParam,
        max_time: selectedMaxTime ?? undefined,
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
  }, [query, selectedCuisine, selectedDietary, selectedOccasion, selectedMaxTime]);

  // Handler to clear search, category, and dietary filters
  const handleResetFilters = () => {
    setQuery("");
    setSelectedCuisine(null);
    setSelectedDietary([]);
    setSelectedOccasion(null);
    setSelectedMaxTime(null);
  };

  const activeFiltersCount =
    selectedDietary.length +
    (selectedOccasion ? 1 : 0) +
    (selectedMaxTime !== null ? 1 : 0);

  return (
    <section>
      <h1>Explore Recipes</h1>
      <p className="muted" style={{ marginBottom: "1rem" }}>
        Discover recipes by title, ingredients, or cuisine.
      </p>

      {/* Search Input & Filter Button */}
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
        <input
          type="search"
          placeholder="Search recipes by title or ingredient..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{ flex: 1 }}
        />
        <button
          type="button"
          onClick={() => setIsFilterDrawerOpen(true)}
          className={`chip ${activeFiltersCount > 0 ? "on" : ""}`}
          style={{ display: "inline-flex", alignItems: "center", gap: "0.4rem", whiteSpace: "nowrap" }}
        >
          <SlidersHorizontal size={16} />
          <span>Filters {activeFiltersCount > 0 ? `(${activeFiltersCount})` : ""}</span>
        </button>
      </div>

      {/* Dietary & Occasion Filter Drawer */}
      <DietaryFilterDrawer
        isOpen={isFilterDrawerOpen}
        onClose={() => setIsFilterDrawerOpen(false)}
        selectedDietary={selectedDietary}
        onDietaryChange={setSelectedDietary}
        selectedOccasion={selectedOccasion}
        onOccasionChange={setSelectedOccasion}
        selectedMaxTime={selectedMaxTime}
        onMaxTimeChange={setSelectedMaxTime}
        onClearAll={handleResetFilters}
        matchingCount={recipes ? recipes.length : undefined}
      />

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
            <RecipeCard key={recipe.id} recipe={recipe} />
          ))}
        </div>
      )}
    </section>
  );
}