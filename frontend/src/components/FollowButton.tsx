import React, { useEffect, useRef, useState } from "react";
import { UserCheck, UserMinus, UserPlus } from "lucide-react";
import { errorText, toggleFollow } from "../services/api";

export interface FollowButtonProps {
  targetUserId: number;
  targetUsername?: string;
  initialFollowing?: boolean;
  initialFollowersCount?: number;
  showCount?: boolean;
  currentUserId?: number;
  size?: "sm" | "md";
  disabled?: boolean;
  className?: string;
  onToggle?: (targetUserId: number, following: boolean, followersCount?: number) => void;
}

export function FollowButton({
  targetUserId,
  targetUsername,
  initialFollowing = false,
  initialFollowersCount = 0,
  showCount = false,
  currentUserId,
  size = "sm",
  disabled = false,
  className = "",
  onToggle,
}: FollowButtonProps) {
  // AC4: Cannot follow oneself
  if (currentUserId !== undefined && currentUserId === targetUserId) {
    return null;
  }

  const [following, setFollowing] = useState<boolean>(initialFollowing);
  const [followersCount, setFollowersCount] = useState<number>(initialFollowersCount);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [isHovered, setIsHovered] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const isSubmittingRef = useRef<boolean>(false);

  useEffect(() => {
    if (!isSubmittingRef.current) {
      setFollowing(initialFollowing);
      setFollowersCount(initialFollowersCount);
    }
  }, [initialFollowing, initialFollowersCount]);

  const handleToggle = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
    if (disabled || isSubmittingRef.current) return;

    setError(null);
    const prevFollowing = following;
    const prevCount = followersCount;

    // Optimistic update (+1 on follow, -1 on unfollow, minimum 0)
    const nextFollowing = !prevFollowing;
    const nextCount = nextFollowing ? prevCount + 1 : Math.max(0, prevCount - 1);

    setFollowing(nextFollowing);
    setFollowersCount(nextCount);
    setIsHovered(false);
    isSubmittingRef.current = true;
    setIsSubmitting(true);

    try {
      const data = await toggleFollow(targetUserId);
      setFollowing(data.following);
      setFollowersCount(data.followers_count);
      onToggle?.(targetUserId, data.following, data.followers_count);
    } catch (err) {
      // Rollback optimistic updates on failure
      setFollowing(prevFollowing);
      setFollowersCount(prevCount);
      setError(errorText(err));
    } finally {
      isSubmittingRef.current = false;
      setIsSubmitting(false);
    }
  };

  const isSmall = size === "sm";
  const labelSuffix = targetUsername ? ` ${targetUsername}` : "";

  return (
    <div className={`inline-flex flex-col items-start ${className}`}>
      <button
        type="button"
        disabled={disabled}
        onClick={handleToggle}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        aria-label={
          following
            ? isHovered
              ? `Unfollow${labelSuffix}`
              : `Following${labelSuffix}`
            : `Follow${labelSuffix}`
        }
        aria-pressed={following}
        aria-busy={isSubmitting}
        className={`group inline-flex items-center rounded-full font-medium transition-all duration-150 focus:outline-none focus-visible:ring-2 focus-visible:ring-rose-500 focus-visible:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed select-none ${
          isSmall ? "px-2.5 py-1 text-xs gap-1.5" : "px-3.5 py-1.5 text-sm gap-2"
        } ${
          following
            ? isHovered
              ? "bg-rose-50 text-rose-600 border border-rose-200"
              : "bg-slate-100 text-slate-700 border border-slate-200 hover:bg-slate-200"
            : "bg-rose-500 text-white hover:bg-rose-600 shadow-sm"
        }`}
      >
        {following ? (
          isHovered ? (
            <UserMinus className={isSmall ? "w-3.5 h-3.5 text-rose-600" : "w-4 h-4 text-rose-600"} />
          ) : (
            <UserCheck className={isSmall ? "w-3.5 h-3.5 text-emerald-600" : "w-4 h-4 text-emerald-600"} />
          )
        ) : (
          <UserPlus className={isSmall ? "w-3.5 h-3.5" : "w-4 h-4"} />
        )}

        <span>
          {following ? (isHovered ? "Unfollow" : "Following") : "Follow"}
        </span>

        {showCount && (
          <span
            className={`tabular-nums font-semibold px-1 rounded ${
              following
                ? isHovered
                  ? "bg-rose-100 text-rose-700"
                  : "bg-slate-200 text-slate-700"
                : "bg-rose-600/60 text-white"
            }`}
          >
            {followersCount}
          </span>
        )}
      </button>

      {error && (
        <span role="alert" className="mt-1 text-xs text-rose-600 select-none">
          {error}
        </span>
      )}
    </div>
  );
}
