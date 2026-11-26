import { Link } from "react-router-dom";
import type { TrendingRecipe } from "../services/api";

/** Shared public fields keep trending and personalized cards consistent. */
export function DiscoveryRecipeCard({ recipe }: { recipe: TrendingRecipe }) {
  return (
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
  );
}
