import { Link } from "react-router-dom";
import { Utensils } from "lucide-react";
import { FollowButton } from "./FollowButton";
import { LikeButton } from "./LikeButton";
import { BookmarkButton } from "./BookmarkButton";
import type { FeedPost } from "../services/api";

export interface FeedCardProps {
  post: FeedPost;
  currentUserId?: number;
  onFollowToggle?: (authorId: number, following: boolean, count?: number) => void;
}

export function FeedCard({ post, currentUserId, onFollowToggle }: FeedCardProps) {
  const formattedDate = new Date(post.created_at).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });

  return (
    <article className="card feed-card mb-6 overflow-hidden border border-slate-200 rounded-xl bg-white shadow-sm">
      {/* Header: Author & Follow Action */}
      <div className="flex items-center justify-between p-4 border-b border-slate-100">
        <div className="flex items-center gap-3">
          {post.author.avatar_url ? (
            <img
              src={post.author.avatar_url}
              alt=""
              className="w-10 h-10 rounded-full object-cover border border-slate-200"
            />
          ) : (
            <div className="w-10 h-10 rounded-full bg-rose-100 text-rose-700 font-bold flex items-center justify-center text-sm border border-rose-200 select-none">
              {post.author.username.charAt(0).toUpperCase()}
            </div>
          )}
          <div>
            <span className="font-semibold text-sm text-slate-900 block">
              {post.author.username}
            </span>
            <time className="text-xs text-slate-500 block">
              {formattedDate}
            </time>
          </div>
        </div>

        <FollowButton
          targetUserId={post.author.id}
          targetUsername={post.author.username}
          currentUserId={currentUserId}
          size="sm"
          onToggle={onFollowToggle}
        />
      </div>

      {/* Media Image */}
      {post.image_url && (
        <div className="bg-slate-900 overflow-hidden">
          <img
            src={post.image_url}
            alt={post.caption || "Food post"}
            className="w-full max-h-[480px] object-cover mx-auto"
            loading="lazy"
          />
        </div>
      )}

      {/* Caption */}
      {post.caption && (
        <div className="p-4 text-sm text-slate-800 leading-relaxed whitespace-pre-wrap">
          {post.caption}
        </div>
      )}

      {/* Linked Recipe Card Banner */}
      {post.recipe && (
        <div className="px-4 pb-3">
          <Link
            to={`/recipes/${post.recipe.id}`}
            className="flex items-center justify-between p-3 rounded-lg bg-amber-50/70 hover:bg-amber-100/70 border border-amber-200/60 transition-colors group text-stone-900"
          >
            <div className="flex items-center gap-2.5">
              <Utensils className="w-4 h-4 text-amber-700 flex-shrink-0" />
              <span className="font-medium text-sm group-hover:text-amber-900">
                {post.recipe.title}
              </span>
            </div>
            <span className="text-xs text-amber-800 font-medium whitespace-nowrap">
              {post.recipe.cook_time_mins} min cook · {post.recipe.difficulty}
            </span>
          </Link>
        </div>
      )}

      {/* Footer Social Actions */}
      <div className="px-4 py-2.5 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
        <LikeButton postId={post.id} />
        <BookmarkButton postId={post.id} />
      </div>
    </article>
  );
}
