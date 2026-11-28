import { useState } from "react";
import { Link } from "react-router-dom";
import { ShoppingCart } from "lucide-react";
import type { RecipeSummary } from "../services/api";
import { RecipeBadges } from "./RecipeBadges";
import { AddToGroceryModal } from "./AddToGroceryModal";

export interface RecipeCardProps {
  recipe: RecipeSummary;
  className?: string;
}

export function RecipeCard({ recipe, className }: RecipeCardProps) {
  const [showGroceryModal, setShowGroceryModal] = useState(false);

  return (
    <>
      <div className={`recipe-card-wrapper relative group ${className || ""}`.trim()}>
        <Link
          to={`/recipes/${recipe.id}`}
          className="recipe-card block"
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

        {/* Quick action: Add to Grocery List */}
        <button
          type="button"
          aria-label={`Add ${recipe.title} to grocery list`}
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setShowGroceryModal(true);
          }}
          className="absolute top-2 right-2 p-1.5 rounded-full bg-white/90 hover:bg-white text-slate-700 hover:text-amber-600 shadow-sm border border-slate-200 transition-colors"
          title="Add to Grocery List"
        >
          <ShoppingCart className="w-4 h-4" />
        </button>
      </div>

      {showGroceryModal && (
        <AddToGroceryModal
          isOpen={showGroceryModal}
          onClose={() => setShowGroceryModal(false)}
          initialRecipeId={recipe.id}
          initialRecipeTitle={recipe.title}
        />
      )}
    </>
  );
}
