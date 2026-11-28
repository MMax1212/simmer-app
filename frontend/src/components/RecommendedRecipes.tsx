import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { DiscoveryEmptyState } from "./DiscoveryEmptyState";
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
  // Match the backend's definition of usable preferences, including hashtag-only input.
  const hasPreferences = user.culinary_preferences.some((value) =>
    value.trim().replace(/^#+/, "").trim().length > 0
  );
  return <RecommendationResults key={profileKey} hasPreferences={hasPreferences} />;
}

function RecommendationResults({ hasPreferences }: { hasPreferences: boolean }) {
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
      {!loading && !error && !hasPreferences && (
        <div className="discovery-guidance">
          {/* Empty preferences invoke rated/newest fallback, not personalized matching. */}
          {recipes.length > 0 && <span className="chip">Community picks</span>}
          <p>Choose your favorite cuisines and interests to personalize these suggestions.</p>
          <Link to="/profile">Choose your preferences</Link>
        </div>
      )}
      {!loading && !error && recipes.length === 0 && (
        <DiscoveryEmptyState message={hasPreferences
          ? "No recommendations found for your preferences."
          : "The community is just getting started."} />
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
