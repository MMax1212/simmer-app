import { useEffect, useRef, useState } from "react";
import { Heart } from "lucide-react";
import { errorText, togglePostLike } from "../services/api";

export interface LikeButtonProps {
  postId: number;
  initialLiked?: boolean;
  initialLikesCount?: number;
  onToggle?: (postId: number, liked: boolean, count: number) => void;
  disabled?: boolean;
}

export function LikeButton({
  postId,
  initialLiked = false,
  initialLikesCount = 0,
  onToggle,
  disabled = false,
}: LikeButtonProps) {
  const [liked, setLiked] = useState<boolean>(initialLiked);
  const [count, setCount] = useState<number>(initialLikesCount);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const isSubmittingRef = useRef<boolean>(false);

  useEffect(() => {
    if (!isSubmittingRef.current) {
      setLiked(initialLiked);
      setCount(initialLikesCount);
    }
  }, [initialLiked, initialLikesCount]);

  const handleToggle = async () => {
    if (disabled || isSubmittingRef.current) return;

    setError(null);
    const prevLiked = liked;
    const prevCount = count;

    // Optimistic update (+1 on like, -1 on unlike, floor at 0)
    const nextLiked = !prevLiked;
    const nextCount = nextLiked ? prevCount + 1 : Math.max(0, prevCount - 1);

    setLiked(nextLiked);
    setCount(nextCount);
    isSubmittingRef.current = true;
    setIsSubmitting(true);

    try {
      const data = await togglePostLike(postId);
      setLiked(data.liked);
      setCount(data.likes_count);
      onToggle?.(postId, data.liked, data.likes_count);
    } catch (err) {
      // Rollback optimistic changes on failure
      setLiked(prevLiked);
      setCount(prevCount);
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
        aria-label={liked ? "Unlike post" : "Like post"}
        aria-pressed={liked}
        aria-busy={isSubmitting}
        className={`group inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-full text-sm font-medium transition-all duration-150 focus:outline-none focus-visible:ring-2 focus-visible:ring-rose-500 focus-visible:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed ${
          liked
            ? "text-rose-600 bg-rose-50 hover:bg-rose-100"
            : "text-slate-600 bg-slate-50 hover:bg-slate-100 hover:text-rose-500"
        }`}
      >
        <Heart
          className={`w-4 h-4 transition-transform duration-150 ${
            liked
              ? "fill-rose-500 text-rose-500 scale-125"
              : "text-slate-400 group-hover:text-rose-400"
          }`}
        />
        <span className="tabular-nums select-none">{count}</span>
      </button>

      {error && (
        <span role="alert" className="mt-1 text-xs text-rose-600 select-none">
          {error}
        </span>
      )}
    </div>
  );
}
