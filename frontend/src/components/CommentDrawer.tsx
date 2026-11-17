import { useContext, useEffect, useRef, useState } from "react";
import { MessageCircle, Send, X } from "lucide-react";
import { AuthContext } from "../context/auth";
import {
  createPostComment,
  errorText,
  getPostComments,
  type Comment,
} from "../services/api";

export interface CommentDrawerProps {
  postId: number;
  isOpen: boolean;
  onClose: () => void;
  initialCommentCount?: number;
  onCommentAdded?: (comment: Comment) => void;
}

export function CommentDrawer({
  postId,
  isOpen,
  onClose,
  initialCommentCount,
  onCommentAdded,
}: CommentDrawerProps) {
  const auth = useContext(AuthContext);
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [content, setContent] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const isSubmittingRef = useRef<boolean>(false);

  // Fetch comments when drawer opens
  useEffect(() => {
    if (!isOpen) return;

    let active = true;
    setLoading(true);
    setError(null);

    getPostComments(postId)
      .then((data) => {
        if (active) {
          setComments(Array.isArray(data) ? data : []);
        }
      })
      .catch((err) => {
        if (active) {
          setError(errorText(err));
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, [postId, isOpen]);

  // Keyboard navigation: Escape key closes drawer
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

  if (!isOpen) {
    return null;
  }

  const trimmed = content.trim();
  const isTooLong = content.length > 1000;
  const isPostDisabled = trimmed.length === 0 || isTooLong || isSubmitting;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isPostDisabled || isSubmittingRef.current) return;

    const textToSubmit = trimmed;
    setError(null);
    setContent("");

    // Optimistic comment insertion
    const tempId = -Date.now();
    const optimisticComment: Comment = {
      id: tempId,
      post_id: postId,
      user_id: auth?.user?.id ?? 1,
      username: auth?.user?.username ?? "current_user",
      avatar_url: auth?.user?.avatar_url ?? null,
      content: textToSubmit,
      created_at: new Date().toISOString(),
    };

    setComments((prev) => [...prev, optimisticComment]);
    isSubmittingRef.current = true;
    setIsSubmitting(true);

    try {
      const serverComment = await createPostComment(postId, textToSubmit);
      // Replace optimistic comment with confirmed server comment
      setComments((prev) =>
        prev.map((c) => (c.id === tempId ? serverComment : c))
      );
      onCommentAdded?.(serverComment);
    } catch (err) {
      // Rollback optimistic comment and restore drafted content
      setComments((prev) => prev.filter((c) => c.id !== tempId));
      setContent(textToSubmit);
      setError(errorText(err));
    } finally {
      isSubmittingRef.current = false;
      setIsSubmitting(false);
    }
  };

  const displayCount =
    comments.length > 0 ? comments.length : initialCommentCount ?? 0;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        data-testid="drawer-backdrop"
        onClick={onClose}
        className="absolute inset-0 bg-black/40 backdrop-blur-xs transition-opacity"
        aria-hidden="true"
      />

      {/* Drawer Dialog */}
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="comment-drawer-title"
        className="fixed inset-y-0 right-0 flex max-w-full pl-10"
      >
        <div className="w-screen max-w-md bg-white shadow-2xl flex flex-col h-full border-l border-slate-200">
          {/* Header */}
          <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
            <div className="flex items-center gap-2">
              <MessageCircle className="w-5 h-5 text-rose-500" />
              <h2
                id="comment-drawer-title"
                className="text-lg font-semibold text-slate-800"
              >
                Comments {displayCount > 0 ? `(${displayCount})` : ""}
              </h2>
            </div>
            <button
              type="button"
              onClick={onClose}
              aria-label="Close comments"
              className="p-1.5 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-rose-500"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Error alert */}
          {error && (
            <div
              role="alert"
              className="mx-4 mt-3 px-3 py-2 text-sm text-rose-700 bg-rose-50 rounded-lg border border-rose-200"
            >
              {error}
            </div>
          )}

          {/* Comment list */}
          <div
            data-testid="comments-list"
            className="flex-1 overflow-y-auto px-5 py-4 space-y-4"
          >
            {loading && (
              <div className="flex justify-center items-center py-12 text-slate-400">
                <span className="text-sm">Loading comments...</span>
              </div>
            )}

            {!loading && comments.length === 0 && (
              <div className="flex flex-col items-center justify-center py-16 text-center text-slate-500">
                <MessageCircle className="w-10 h-10 text-slate-300 mb-2 stroke-1" />
                <p className="text-sm font-medium">
                  No comments yet. Be the first to share your thoughts!
                </p>
              </div>
            )}

            {!loading &&
              comments.map((comment) => (
                <div
                  key={comment.id}
                  className="flex items-start gap-3 text-sm group"
                >
                  {comment.avatar_url ? (
                    <img
                      src={comment.avatar_url}
                      alt={comment.username}
                      className="w-8 h-8 rounded-full object-cover shrink-0 border border-slate-200"
                    />
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-rose-100 text-rose-600 font-semibold flex items-center justify-center shrink-0 text-xs uppercase">
                      {comment.username.slice(0, 2)}
                    </div>
                  )}

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="font-semibold text-slate-800 text-xs">
                        {comment.username}
                      </span>
                      <span className="text-slate-400 text-xs">
                        {comment.created_at
                          ? new Date(comment.created_at).toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                            })
                          : ""}
                      </span>
                    </div>
                    <p className="text-slate-700 leading-relaxed break-words">
                      {comment.content}
                    </p>
                  </div>
                </div>
              ))}
          </div>

          {/* Sticky bottom input */}
          <form
            onSubmit={handleSubmit}
            className="p-4 border-t border-slate-100 bg-slate-50/50"
          >
            <div className="relative">
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Add a comment..."
                rows={2}
                maxLength={1000}
                className="w-full resize-none rounded-xl border border-slate-200 bg-white p-3 pr-10 text-sm text-slate-800 placeholder-slate-400 focus:border-rose-400 focus:outline-none focus:ring-2 focus:ring-rose-100 transition-all"
              />
            </div>

            <div className="flex items-center justify-between mt-2 pt-1">
              <span
                className={`text-xs select-none ${
                  isTooLong ? "text-rose-600 font-medium" : "text-slate-400"
                }`}
              >
                {content.length} / 1000
              </span>

              <button
                type="submit"
                disabled={isPostDisabled}
                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-rose-600 text-white text-xs font-semibold hover:bg-rose-700 active:bg-rose-800 disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-xs"
              >
                <Send className="w-3.5 h-3.5" />
                <span>Post</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
