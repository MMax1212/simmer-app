import { useState, type KeyboardEvent } from "react";

interface TagInputProps {
  tags: string[];
  onChange: (newTags: string[]) => void;
  suggestions?: string[];
}

export function TagInput({ tags, onChange, suggestions = ["#quick", "#dinner", "#italian", "#healthy", "#comfortfood"] }: TagInputProps) {
  const [input, setInput] = useState("");

  const addTag = (raw: string) => {
    let tag = raw.trim();
    if (!tag) return;
    if (!tag.startsWith("#")) tag = `#${tag}`;
    tag = tag.toLowerCase().replace(/\s+/g, ""); // No spaces in hashtags

    if (!tags.includes(tag)) {
      onChange([...tags, tag]);
    }
    setInput("");
  };

  const removeTag = (indexToRemove: number) => {
    onChange(tags.filter((_, i) => i !== indexToRemove));
  };

  const onKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addTag(input);
    } else if (e.key === "Backspace" && !input && tags.length > 0) {
      removeTag(tags.length - 1);
    }
  };

  return (
    <div className="flex flex-col gap-2">
      <label>
        Category Tags
        <span className="text-xs text-stone-500 font-normal"> (Type a hashtag and press Enter)</span>
      </label>

      {/* Selected Tag Badges */}
      <div className="flex flex-wrap gap-2 items-center p-2 border border-stone-200 rounded-lg bg-white min-h-[44px]">
        {tags.map((tag, idx) => (
          <span
            key={idx}
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-orange-100 text-orange-800 border border-orange-200"
          >
            {tag}
            <button
              type="button"
              className="text-orange-600 hover:text-orange-900 font-bold leading-none cursor-pointer p-0 bg-transparent border-0"
              onClick={() => removeTag(idx)}
              aria-label={`Remove ${tag}`}
            >
              ×
            </button>
          </span>
        ))}

        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          onBlur={() => addTag(input)}
          placeholder={tags.length === 0 ? "Add tags (e.g. #japanese, #brunch)..." : "Add more..."}
          className="flex-1 min-w-[140px] border-none outline-none p-1 text-sm bg-transparent"
        />
      </div>

      {/* Quick-Click Suggestions */}
      {suggestions.length > 0 && (
        <div className="flex flex-wrap gap-1.5 items-center mt-1">
          <span className="text-xs text-stone-400">Suggestions:</span>
          {suggestions
            .filter((s) => !tags.includes(s))
            .slice(0, 6)
            .map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                className="text-xs px-2 py-0.5 rounded-full border border-stone-200 bg-stone-50 text-stone-600 hover:bg-stone-100 cursor-pointer"
                onClick={() => addTag(suggestion)}
              >
                + {suggestion}
              </button>
            ))}
        </div>
      )}
    </div>
  );
}