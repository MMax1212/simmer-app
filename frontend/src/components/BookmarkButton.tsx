import { useEffect, useRef, useState } from "react";
import { Bookmark } from "lucide-react";
import { errorText, togglePostBookmark } from "../services/api";


export interface BookmarkButtonProps {
  postId: number;
  initialBookmarked?: boolean;
  onToggle?: (postId: number, bookmarked: boolean) => void;
  disabled?: boolean;
}

export function BookmarkButton({
  postId,
  initialBookmarked = false,
  onToggle,
  disabled = false,
}: BookmarkButtonProps) {
  const [bookmarked, setBookmarked] = useState<boolean>(initialBookmarked);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const isSubmittingRef = useRef<boolean>(false);
  useEffect(() => {
    if (!isSubmittingRef.current) {
      setBookmarked(initialBookmarked);
    }
  }, [initialBookmarked]);
  const handleToggle = async () => {
    if (disabled || isSubmittingRef.current) return;
    setError(null);
    const prevBookmarked = bookmarked;
    // 1. Instant Optimistic update
    const nextBookmarked = !prevBookmarked;
    setBookmarked(nextBookmarked);
    isSubmittingRef.current = true;
    setIsSubmitting(true);
    try {
      // 2. Call the backend API
      const data = await togglePostBookmark(postId);
      const isSaved = data.bookmarked ?? data.bookmark;
      setBookmarked(isSaved);
      onToggle?.(postId, isSaved);
    } catch (err) {
      // 3. Roll back if network fails
      setBookmarked(prevBookmarked);
      setError(errorText(err));
    } finally {
      isSubmittingRef.current = false;
      setIsSubmitting(false);
    }
  };
  return (
    <div className="inline-flex flex-col items-start">
      <button
        type="button"
        disabled={disabled}
        onClick={handleToggle}
        aria-label={bookmarked ? "Remove bookmark" : "Bookmark post"}
        aria-pressed={bookmarked}
        aria-busy={isSubmitting}
        className={`group inline-flex items-center justify-center p-2 rounded-full text-sm font-medium transition-all duration-150 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed ${
          bookmarked
            ? "text-amber-600 bg-amber-50 hover:bg-amber-100"
            : "text-slate-600 bg-slate-50 hover:bg-slate-100 hover:text-amber-500"
        }`}
      >
        <Bookmark
          className={`w-5 h-5 transition-transform duration-150 ${
            bookmarked
              ? "fill-amber-500 text-amber-500 scale-110"
              : "text-slate-400 group-hover:text-amber-500"
          }`}
        />
      </button>
      {error && (
        <span role="alert" className="mt-1 text-xs text-rose-600 select-none">
          {error}
        </span>
      )}
    </div>
  );
}
