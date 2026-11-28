import { Link } from "react-router-dom";
import type { RecipeSummary } from "../services/api";
import { RecipeBadges } from "./RecipeBadges";

export interface RecipeCardProps {
  recipe: RecipeSummary;
  className?: string;
}

export function RecipeCard({ recipe, className }: RecipeCardProps) {
  return (
    <Link
      to={`/recipes/${recipe.id}`}
      className={`recipe-card ${className || ""}`.trim()}
    >
      {recipe.image_url && (
        <img
          src={recipe.image_url}
          alt={recipe.title}
          style={{
            width: "100%",
            height: "140px",
            objectFit: "cover",
            borderRadius: "var(--radius)",
          }}
        />
      )}
      <h3>{recipe.title}</h3>
      {recipe.cuisine && <span className="small muted">Cuisine: {recipe.cuisine}</span>}
      <p className="small muted">
        By {recipe.author_username} · {recipe.cook_time_mins} min · {recipe.difficulty}
      </p>
      {recipe.tags && recipe.tags.length > 0 && (
        <RecipeBadges tags={recipe.tags} ariaLabel={`Badges for ${recipe.title}`} />
      )}
    </Link>
  );
}
