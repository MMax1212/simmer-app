import type { ElementType } from "react";
import { Calendar, Clock, Flame, Heart, Smile } from "lucide-react";

export type BadgeCategory = "dietary" | "occasion" | "general";

export interface ClassifiedTag {
  raw: string;
  category: BadgeCategory;
  label: string;
  icon?: ElementType;
  variantClass: string;
}

const DIETARY_TAG_MAP: Record<string, { label: string; variant: string }> = {
  vegan: { label: "Vegan", variant: "badge-plant" },
  vegetarian: { label: "Vegetarian", variant: "badge-plant" },
  "gluten-free": { label: "Gluten-Free", variant: "badge-grain" },
  keto: { label: "Keto", variant: "badge-grain" },
  "low-carb": { label: "Low-Carb", variant: "badge-grain" },
  "dairy-free": { label: "Dairy-Free", variant: "badge-allergen" },
  "nut-free": { label: "Nut-Free", variant: "badge-allergen" },
};

const OCCASION_TAG_MAP: Record<string, { label: string; icon: ElementType }> = {
  "quick-dinner": { label: "Quick Dinner", icon: Clock },
  "under-30-mins": { label: "Under 30 Mins", icon: Clock },
  "date-night": { label: "Date Night", icon: Heart },
  "meal-prep": { label: "Meal Prep", icon: Calendar },
  "comfort-food": { label: "Comfort Food", icon: Flame },
  "kid-friendly": { label: "Kid-Friendly", icon: Smile },
};

export function classifyTag(rawTag: string): ClassifiedTag {
  const normalized = rawTag.trim().toLowerCase().replace(/^#/, "");

  if (DIETARY_TAG_MAP[normalized]) {
    const config = DIETARY_TAG_MAP[normalized];
    return {
      raw: rawTag,
      category: "dietary",
      label: config.label,
      variantClass: `badge-dietary ${config.variant}`,
    };
  }

  if (OCCASION_TAG_MAP[normalized]) {
    const config = OCCASION_TAG_MAP[normalized];
    return {
      raw: rawTag,
      category: "occasion",
      label: config.label,
      icon: config.icon,
      variantClass: "badge-occasion",
    };
  }

  return {
    raw: rawTag,
    category: "general",
    label: rawTag.startsWith("#") ? rawTag : `#${rawTag}`,
    variantClass: "badge-general",
  };
}

export interface RecipeBadgesProps {
  tags?: string[];
  className?: string;
  ariaLabel?: string;
}

export function RecipeBadges({ tags, className, ariaLabel }: RecipeBadgesProps) {
  if (!tags || tags.length === 0) {
    return null;
  }

  const classified = tags.map(classifyTag);

  return (
    <div
      className={`dietary-badges ${className || ""}`.trim()}
      role="group"
      aria-label={ariaLabel || "Recipe dietary and occasion tags"}
    >
      {classified.map((item, index) => {
        const IconComponent = item.icon;
        const ariaLabelText =
          item.category === "dietary"
            ? `Dietary: ${item.label}`
            : item.category === "occasion"
            ? `Occasion: ${item.label}`
            : `Tag: ${item.label}`;

        return (
          <span
            key={`${item.raw}-${index}`}
            className={`dietary-badge ${item.variantClass}`}
            aria-label={ariaLabelText}
          >
            {IconComponent && <IconComponent size={13} aria-hidden="true" />}
            <span>{item.label}</span>
          </span>
        );
      })}
    </div>
  );
}
