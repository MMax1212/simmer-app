import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api, errorText, type TrendingRecipe } from "../services/api";

const TRENDING_CARD_LIMIT = 5;

/** A native scroll list supports touch, keyboard and buttons without auto-rotation. */
export function TrendingCarousel() {
  const [recipes, setRecipes] = useState<TrendingRecipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);
  const list = useRef<HTMLUListElement>(null);

  useEffect(() => {
    // Ignore stale completions after unmount or retry; StrictMode may run effects twice.
    let active = true;
    setLoading(true);
    setError(null);
    api.getTrendingRecipes(TRENDING_CARD_LIMIT)
      .then((items) => { if (active) setRecipes(items); })
      .catch((reason) => { if (active) setError(errorText(reason)); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [attempt]);

  function scrollPage(direction: number) {
    const element = list.current;
    // No timed or smooth motion: scrolling remains under the reader's control.
    element?.scrollBy({ left: direction * element.clientWidth, behavior: "auto" });
  }

  return (
    <section aria-labelledby="trending-title" className="trending-section">
      <h2 id="trending-title">Trending Recipes This Week</h2>
      {loading && <p role="status">Loading trending recipes…</p>}
      {!loading && error && (
        <div>
          <p role="alert">Could not load trending recipes: {error}</p>
          <button type="button" onClick={() => setAttempt((value) => value + 1)}>
            Retry trending recipes
          </button>
        </div>
      )}
      {!loading && !error && recipes.length === 0 && <p>No recipes to discover yet.</p>}
      {!loading && !error && recipes.length > 0 && (
        <>
          <div className="row">
            <button type="button" aria-label="Previous trending recipes"
              onClick={() => scrollPage(-1)}>Previous</button>
            <button type="button" aria-label="Next trending recipes"
              onClick={() => scrollPage(1)}>Next</button>
          </div>
          {/* Preserve server ranking, including its cold-start fallback ordering. */}
          <ul ref={list} className="trending-list" aria-label="Trending recipes" tabIndex={0}>
            {recipes.map((recipe) => (
              <li key={recipe.id} className="trending-item">
                <Link to={`/recipes/${recipe.id}`} className="recipe-card trending-card">
                  {recipe.image_url ? (
                    <img src={recipe.image_url} alt="" loading="lazy"
                      onError={(event) => {
                        // Hide unavailable photos without hiding the recipe's readable title.
                        event.currentTarget.hidden = true;
                      }} />
                  ) : <span className="trending-placeholder">No photo yet</span>}
                  <h3>{recipe.title}</h3>
                  <p className="small muted">
                    By {recipe.author_username} · {recipe.cook_time_mins}
                    {" min cook"}</p>
                  <p className="small">{recipe.cuisine ? `${recipe.cuisine} · ` : ""}
                    {recipe.difficulty}</p>
                  <p className="small">{recipe.likes_count} likes · {recipe.completed_count} cooked</p>
                </Link>
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  );
}
