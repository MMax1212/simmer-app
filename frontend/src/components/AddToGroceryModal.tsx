import { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ShoppingCart, X, AlertCircle } from "lucide-react";
import { AuthContext } from "../context/auth";
import {
  api,
  errorText,
  type RecipeSummary,
  type GroceryList,
} from "../services/api";

export interface AddToGroceryModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialRecipeId?: number;
  initialRecipeTitle?: string;
  onSuccess?: (list: GroceryList) => void;
}

export function AddToGroceryModal({
  isOpen,
  onClose,
  initialRecipeId,
  initialRecipeTitle,
  onSuccess,
}: AddToGroceryModalProps) {
  const auth = useContext(AuthContext);
  const user = auth?.user ?? null;
  const navigate = useNavigate();

  const [availableRecipes, setAvailableRecipes] = useState<RecipeSummary[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>(
    initialRecipeId ? [initialRecipeId] : []
  );
  const [title, setTitle] = useState("Weekly Meal Prep");
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize selected recipes when opened
  useEffect(() => {
    if (isOpen && initialRecipeId && !selectedIds.includes(initialRecipeId)) {
      setSelectedIds([initialRecipeId]);
    }
  }, [isOpen, initialRecipeId]);

  // Load available recipes for multi-selection
  useEffect(() => {
    if (!isOpen) return;
    let active = true;
    setIsLoading(true);

    api
      .searchRecipes({ limit: 50 })
      .then((res) => {
        if (active) {
          const list: RecipeSummary[] = [...(res.items || [])];
          // Ensure initialRecipe is in available list if provided
          if (
            initialRecipeId &&
            !list.some((r: RecipeSummary) => r.id === initialRecipeId) &&
            initialRecipeTitle
          ) {
            list.unshift({
              id: initialRecipeId,
              title: initialRecipeTitle,
              cook_time_mins: 0,
              difficulty: "easy",
              author_username: "",
            } as RecipeSummary);
          }
          setAvailableRecipes(list);
          setIsLoading(false);
        }
      })
      .catch((err) => {
        if (active) {
          setError(errorText(err));
          setIsLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, [isOpen, initialRecipeId, initialRecipeTitle]);

  if (!isOpen) return null;

  function toggleRecipe(id: number) {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((rId) => rId !== id) : [...prev, id]
    );
  }

  async function handleGenerate(e: React.FormEvent) {
    e.preventDefault();
    if (selectedIds.length === 0) return;

    if (!user) {
      sessionStorage.setItem("saved_grocery_recipe_ids", JSON.stringify(selectedIds));
      setError("Please log in or create an account to save grocery checklists");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const groceryList = await api.generateGroceryList({
        recipe_ids: selectedIds,
        title: title.trim() || "My Grocery List",
      });
      if (onSuccess) {
        onSuccess(groceryList);
      }
      onClose();
      navigate("/grocery");
    } catch (err) {
      setError(errorText(err));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Add to Grocery List"
      className="modal-backdrop fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
    >
      <div className="card modal-content bg-white w-full max-w-lg rounded-xl shadow-xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <ShoppingCart className="w-5 h-5 text-amber-600" />
            <h2 className="text-lg font-bold text-slate-900">Add to Grocery List</h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close modal"
            className="p-1 rounded-lg hover:bg-slate-100 text-slate-500 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Form */}
        <form onSubmit={handleGenerate} className="flex-1 overflow-y-auto p-4 space-y-4">
          {error && (
            <div
              role="alert"
              className="p-3 text-sm rounded-lg bg-rose-50 border border-rose-200 text-rose-700 flex items-start gap-2"
            >
              <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label
              htmlFor="grocery-title"
              className="block text-xs font-semibold uppercase text-slate-600 mb-1"
            >
              Checklist Title
            </label>
            <input
              id="grocery-title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., Weekly Meal Prep"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-amber-500"
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold uppercase text-slate-600">
                Select Recipes ({selectedIds.length} selected)
              </span>
              <span className="text-xs text-amber-700 font-medium">
                Aggregates matching ingredients
              </span>
            </div>

            {isLoading ? (
              <p className="text-sm text-slate-500 py-4 text-center">Loading recipes…</p>
            ) : (
              <div className="space-y-1.5 max-h-56 overflow-y-auto border border-slate-200 rounded-lg p-2 bg-slate-50/50">
                {availableRecipes.map((r) => {
                  const isChecked = selectedIds.includes(r.id);
                  return (
                    <label
                      key={r.id}
                      className={`flex items-center justify-between p-2 rounded-lg cursor-pointer transition-colors text-sm border ${
                        isChecked
                          ? "bg-amber-50 border-amber-300 text-amber-950 font-medium"
                          : "bg-white border-slate-200 hover:bg-slate-50 text-slate-800"
                      }`}
                    >
                      <div className="flex items-center gap-2.5 min-w-0">
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => toggleRecipe(r.id)}
                          className="rounded border-slate-300 text-amber-600 focus:ring-amber-500"
                        />
                        <span className="truncate">{r.title}</span>
                      </div>
                      <span className="text-xs text-slate-500 ml-2 whitespace-nowrap">
                        {r.cook_time_mins}m · {r.difficulty}
                      </span>
                    </label>
                  );
                })}
              </div>
            )}
          </div>

          <div className="pt-2 flex items-center justify-end gap-2 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm text-slate-600 hover:text-slate-800 rounded-lg hover:bg-slate-100 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={selectedIds.length === 0 || isSubmitting}
              className="px-4 py-2 text-sm font-medium text-white bg-amber-600 hover:bg-amber-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg shadow-sm transition-colors flex items-center gap-1.5"
            >
              {isSubmitting ? "Generating…" : "Generate Shopping List"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
