import { useEffect, useState } from "react";
import { useAuth } from "../context/auth";
import { api, errorText, type TrendingRecipe } from "../services/api";
import { DiscoveryRecipeCard } from "./DiscoveryRecipeCard";

const RECOMMENDATION_LIMIT = 5;

/** Private discovery is mounted only after authentication has resolved. */
export function RecommendedRecipes() {
  const { user, loading } = useAuth();
  if (loading || !user) return null;

  // Key the request state to its profile, not just its user ID. This synchronously
  // removes old cards on preference edits/account changes before the next effect runs.
  const profileKey = JSON.stringify([user.id, [...user.culinary_preferences].sort()]);
  return <RecommendationResults key={profileKey} />;
}

function RecommendationResults() {
  const [recipes, setRecipes] = useState<TrendingRecipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    // Logout, profile changes and retries invalidate the old request. A late response
    // must never replace the current account's cards or restore a previous error.
    let active = true;
    setLoading(true);
    setError(null);
    api.getRecommendedRecipes(RECOMMENDATION_LIMIT)
      .then((items) => { if (active) setRecipes(items); })
      .catch((reason) => { if (active) setError(errorText(reason)); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [attempt]);

  return (
    <section aria-labelledby="recommendations-title">
      <h2 id="recommendations-title">Recommended for You</h2>
      {/* The backend may return top-rated fallback, so do not label every card a match. */}
      <p className="muted">Recipe suggestions for your next meal.</p>
      {loading && <p role="status">Loading recommendations…</p>}
      {!loading && error && (
        <div>
          <p role="alert">Could not load recommendations: {error}</p>
          <button type="button" onClick={() => setAttempt((value) => value + 1)}>
            Retry recommendations
          </button>
        </div>
      )}
      {!loading && !error && recipes.length === 0 && (
        <p>No recommendations found for your preferences.</p>
      )}
      {!loading && !error && recipes.length > 0 && (
        <ul className="recipe-grid recommendation-list" aria-label="Recommended recipes">
          {recipes.map((recipe) => (
            <li key={recipe.id}><DiscoveryRecipeCard recipe={recipe} /></li>
          ))}
        </ul>
      )}
    </section>
  );
}
