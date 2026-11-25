import { useEffect } from "react";
import { Clock, RotateCcw, SlidersHorizontal, Utensils, X } from "lucide-react";

export interface DietaryFilterDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  selectedDietary: string[];
  onDietaryChange: (tags: string[]) => void;
  selectedOccasion: string | null;
  onOccasionChange: (occasion: string | null) => void;
  selectedMaxTime: number | null;
  onMaxTimeChange: (time: number | null) => void;
  onClearAll: () => void;
  matchingCount?: number;
}

export const DIETARY_OPTIONS = [
  { tag: "#vegan", label: "Vegan" },
  { tag: "#vegetarian", label: "Vegetarian" },
  { tag: "#gluten-free", label: "Gluten-Free" },
  { tag: "#keto", label: "Keto" },
  { tag: "#low-carb", label: "Low-Carb" },
  { tag: "#dairy-free", label: "Dairy-Free" },
  { tag: "#nut-free", label: "Nut-Free" },
];

export const OCCASION_OPTIONS = [
  { tag: "#quick-dinner", label: "Quick Dinner" },
  { tag: "#under-30-mins", label: "Under 30 Mins" },
  { tag: "#date-night", label: "Date Night" },
  { tag: "#meal-prep", label: "Meal Prep" },
  { tag: "#comfort-food", label: "Comfort Food" },
  { tag: "#kid-friendly", label: "Kid-Friendly" },
];

export const MAX_TIME_OPTIONS = [
  { mins: 15, label: "≤ 15 mins" },
  { mins: 30, label: "≤ 30 mins" },
  { mins: 45, label: "≤ 45 mins" },
  { mins: 60, label: "≤ 60 mins" },
];

export function DietaryFilterDrawer({
  isOpen,
  onClose,
  selectedDietary,
  onDietaryChange,
  selectedOccasion,
  onOccasionChange,
  selectedMaxTime,
  onMaxTimeChange,
  onClearAll,
  matchingCount,
}: DietaryFilterDrawerProps) {
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const toggleDietary = (tag: string) => {
    if (selectedDietary.includes(tag)) {
      onDietaryChange(selectedDietary.filter((t) => t !== tag));
    } else {
      onDietaryChange([...selectedDietary, tag]);
    }
  };

  const toggleOccasion = (tag: string) => {
    if (selectedOccasion === tag) {
      onOccasionChange(null);
    } else {
      onOccasionChange(tag);
    }
  };

  const toggleMaxTime = (mins: number) => {
    if (selectedMaxTime === mins) {
      onMaxTimeChange(null);
    } else {
      onMaxTimeChange(mins);
    }
  };

  const activeFiltersCount =
    selectedDietary.length +
    (selectedOccasion ? 1 : 0) +
    (selectedMaxTime !== null ? 1 : 0);

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        data-testid="filter-drawer-backdrop"
        onClick={onClose}
        className="absolute inset-0 bg-black/40 backdrop-blur-xs transition-opacity"
        aria-hidden="true"
      />

      {/* Drawer Dialog */}
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Filter Recipes"
        className="fixed inset-y-0 right-0 flex max-w-full pl-10"
      >
        <div className="w-screen max-w-md bg-white shadow-2xl flex flex-col h-full border-l border-slate-200">
          {/* Header */}
          <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
            <div className="flex items-center gap-2">
              <SlidersHorizontal className="w-5 h-5 text-orange-500" />
              <h2 className="text-lg font-semibold text-slate-800">
                Filter Recipes {activeFiltersCount > 0 ? `(${activeFiltersCount})` : ""}
              </h2>
            </div>
            <button
              type="button"
              onClick={onClose}
              aria-label="Close filter drawer"
              className="p-1.5 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Body Content */}
          <div className="flex-1 overflow-y-auto p-5 space-y-6">
            {/* Dietary Preferences Section */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Utensils className="w-4 h-4 text-orange-600" />
                <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wider">
                  Dietary Preferences
                </h3>
              </div>
              <p className="text-xs text-slate-500 mb-3">
                Select one or more requirements (strict match):
              </p>
              <div className="chips" role="group" aria-label="Dietary preferences">
                {DIETARY_OPTIONS.map((opt) => {
                  const isActive = selectedDietary.includes(opt.tag);
                  return (
                    <button
                      key={opt.tag}
                      type="button"
                      className={`chip ${isActive ? "on" : ""}`}
                      onClick={() => toggleDietary(opt.tag)}
                    >
                      {opt.label}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Occasions Section */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-sm font-semibold text-slate-700 uppercase tracking-wider">
                  Occasions
                </span>
              </div>
              <p className="text-xs text-slate-500 mb-3">
                Find recipes tailored to specific dining moments:
              </p>
              <div className="chips" role="group" aria-label="Occasions">
                {OCCASION_OPTIONS.map((opt) => {
                  const isActive = selectedOccasion === opt.tag;
                  return (
                    <button
                      key={opt.tag}
                      type="button"
                      className={`chip ${isActive ? "on" : ""}`}
                      onClick={() => toggleOccasion(opt.tag)}
                    >
                      {opt.label}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Max Cooking Time Section */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Clock className="w-4 h-4 text-orange-600" />
                <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wider">
                  Max Cooking Time
                </h3>
              </div>
              <p className="text-xs text-slate-500 mb-3">
                Combined prep and cooking time limit:
              </p>
              <div className="chips" role="group" aria-label="Max cooking time">
                {MAX_TIME_OPTIONS.map((opt) => {
                  const isActive = selectedMaxTime === opt.mins;
                  return (
                    <button
                      key={opt.mins}
                      type="button"
                      className={`chip ${isActive ? "on" : ""}`}
                      onClick={() => toggleMaxTime(opt.mins)}
                    >
                      {opt.label}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Footer Controls */}
          <div className="p-4 border-t border-slate-100 bg-slate-50 flex items-center justify-between gap-3">
            <button
              type="button"
              onClick={onClearAll}
              className="flex items-center gap-1.5 text-xs text-slate-600 hover:text-slate-900 font-medium px-3 py-2 rounded-md hover:bg-slate-200 transition-colors cursor-pointer"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Clear all filters
            </button>

            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white text-sm font-medium rounded-md shadow-sm transition-colors cursor-pointer"
            >
              Apply Filters {matchingCount !== undefined ? `(${matchingCount})` : ""}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
