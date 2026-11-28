import type { ElementType } from "react";
import { Calendar, Clock, Flame, Heart, Sparkles, Utensils } from "lucide-react";
import type { SearchFilters } from "../services/api";

export interface QuickFilterPreset {
  id: string;
  title: string;
  description: string;
  icon: ElementType;
  filters: Partial<SearchFilters>;
}

export const QUICK_FILTER_PRESETS: QuickFilterPreset[] = [
  {
    id: "under-30-mins",
    title: "Under 30 Mins",
    description: "Fast meals ready in half an hour",
    icon: Clock,
    filters: { max_time: 30 },
  },
  {
    id: "plant-based",
    title: "Plant-Based",
    description: "Delicious vegetarian & vegan dishes",
    icon: Sparkles,
    filters: { dietary: "vegan,vegetarian" },
  },
  {
    id: "date-night",
    title: "Date Night Dinner",
    description: "Special meals made to impress",
    icon: Heart,
    filters: { occasion: "date-night" },
  },
  {
    id: "meal-prep",
    title: "Meal Prep",
    description: "Cook once, eat all week",
    icon: Calendar,
    filters: { occasion: "meal-prep" },
  },
  {
    id: "comfort-food",
    title: "Comfort Food",
    description: "Warm, hearty, and satisfying",
    icon: Flame,
    filters: { occasion: "comfort-food" },
  },
  {
    id: "low-carb",
    title: "Low-Carb & Keto",
    description: "High protein, low carbohydrate",
    icon: Utensils,
    filters: { dietary: "keto,low-carb" },
  },
];

export interface QuickFilterPresetsProps {
  selectedPresetId: string | null;
  onSelectPreset: (preset: QuickFilterPreset | null) => void;
  className?: string;
}

export function QuickFilterPresets({
  selectedPresetId,
  onSelectPreset,
  className,
}: QuickFilterPresetsProps) {
  return (
    <section className={`quick-presets-section ${className || ""}`.trim()}>
      <div className="flex items-center justify-between mb-3">
        <div>
          <h2 className="text-lg font-bold">Explore Curated Collections</h2>
          <p className="text-xs text-stone-500">
            Quickly filter delicious meals by your dietary lifestyle or occasion.
          </p>
        </div>
        {selectedPresetId && (
          <button
            type="button"
            className="link-button text-xs font-semibold text-rose-600 hover:text-rose-700"
            onClick={() => onSelectPreset(null)}
          >
            Clear collection filter
          </button>
        )}
      </div>

      <div
        className="quick-presets-grid"
        role="group"
        aria-label="Quick filter presets"
      >
        {QUICK_FILTER_PRESETS.map((preset) => {
          const isActive = selectedPresetId === preset.id;
          const Icon = preset.icon;

          return (
            <button
              key={preset.id}
              type="button"
              className={`quick-preset-card ${isActive ? "active" : ""}`}
              aria-pressed={isActive}
              onClick={() => onSelectPreset(isActive ? null : preset)}
            >
              <div className="quick-preset-icon-wrap" aria-hidden="true">
                <Icon size={20} />
              </div>
              <div className="quick-preset-content">
                <span className="quick-preset-title">{preset.title}</span>
                <span className="quick-preset-desc">{preset.description}</span>
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}
