import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { ChevronLeft, ChevronRight, Loader2, Sparkles } from "lucide-react";
import { useAuth } from "../context/auth";
import { errorText, getSuggestedCooks, type UserSearchResultItem } from "../services/api";
import { FollowButton } from "./FollowButton";

export function SuggestedCooksCarousel() {
  let user = null;
  try {
    user = useAuth()?.user;
  } catch {
    user = null;
  }
  const [cooks, setCooks] = useState<UserSearchResultItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);

  const listRef = useRef<HTMLUListElement>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);

    getSuggestedCooks(10)
      .then((items) => {
        if (active) {
          const raw = Array.isArray(items)
            ? items
            : Array.isArray((items as unknown as { items?: UserSearchResultItem[] })?.items)
            ? (items as unknown as { items: UserSearchResultItem[] }).items
            : [];
          const validCooks = raw.filter(
            (c): c is UserSearchResultItem => Boolean(c && typeof c === "object" && typeof (c as UserSearchResultItem).username === "string")
          );
          setCooks(validCooks);
        }
      })
      .catch((err) => {
        if (active) setError(errorText(err));
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [attempt]);

  const scroll = (direction: -1 | 1) => {
    if (listRef.current) {
      listRef.current.scrollBy({ left: direction * 280, behavior: "smooth" });
    }
  };

  const handleFollowToggle = (targetUserId: number, following: boolean, followersCount?: number) => {
    setCooks((prev) =>
      prev.map((cook) =>
        cook.id === targetUserId
          ? {
              ...cook,
              is_following: following,
              followers_count:
                followersCount ??
                (following ? cook.followers_count + 1 : Math.max(0, cook.followers_count - 1)),
            }
          : cook
      )
    );
  };

  if (loading && cooks.length === 0) {
    return (
      <section aria-labelledby="suggested-cooks-title" className="my-8">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="h-5 w-5 text-orange-600" />
          <h2 id="suggested-cooks-title" className="text-xl font-bold text-stone-900">
            Suggested Cooks to Follow
          </h2>
        </div>
        <div className="flex items-center justify-center p-8 bg-stone-50 rounded-2xl border border-stone-200 text-stone-500 text-sm gap-2">
          <Loader2 className="h-5 w-5 animate-spin text-orange-600" />
          <span>Finding culinary creators for you...</span>
        </div>
      </section>
    );
  }

  if (error && cooks.length === 0) {
    return (
      <section aria-labelledby="suggested-cooks-title" className="my-8">
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-center text-sm text-red-700 flex flex-col items-center gap-2">
          <p>Could not load suggested cooks: {error}</p>
          <button
            type="button"
            onClick={() => setAttempt((v) => v + 1)}
            className="px-3 py-1 bg-red-600 text-white rounded-md text-xs font-semibold hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </section>
    );
  }

  if (!loading && (!Array.isArray(cooks) || cooks.length === 0)) {
    return null;
  }

  return (
    <section aria-labelledby="suggested-cooks-title" className="my-8">
      {/* Section Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-orange-600" />
          <h2 id="suggested-cooks-title" className="text-xl font-bold text-stone-900">
            Suggested Cooks to Follow
          </h2>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/friends"
            className="text-sm font-semibold text-orange-600 hover:text-orange-700 transition-colors"
          >
            Explore all
          </Link>

          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => scroll(-1)}
              aria-label="Previous suggested cooks"
              className="p-1.5 rounded-full border border-stone-300 text-stone-600 hover:bg-stone-100 transition-colors"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button
              type="button"
              onClick={() => scroll(1)}
              aria-label="Next suggested cooks"
              className="p-1.5 rounded-full border border-stone-300 text-stone-600 hover:bg-stone-100 transition-colors"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Horizontal Carousel */}
      <ul
        ref={listRef}
        role="region"
        aria-label="Suggested cooks list"
        tabIndex={0}
        className="flex gap-4 overflow-x-auto pb-3 pt-1 scroll-smooth focus:outline-none"
      >
        {Array.isArray(cooks) && cooks.map((cook) => {
          const username = cook?.username || "";
          return (
            <li
              key={cook.id}
              data-testid={`suggested-cook-card-${cook.id}`}
              className="w-56 flex-shrink-0 bg-white border border-stone-200 rounded-2xl p-4 shadow-sm hover:shadow-md transition-shadow flex flex-col items-center text-center justify-between"
            >
              <div className="flex flex-col items-center w-full">
                {cook.avatar_url ? (
                  <img
                    src={cook.avatar_url}
                    alt={username}
                    className="w-16 h-16 rounded-full object-cover border-2 border-stone-100 mb-3"
                  />
                ) : (
                  <div className="w-16 h-16 rounded-full bg-orange-100 text-orange-700 flex items-center justify-center font-bold text-lg uppercase border-2 border-orange-200 mb-3">
                    {username ? username.slice(0, 2).toUpperCase() : "??"}
                  </div>
                )}

                <Link
                  to={`/friends?q=${encodeURIComponent(username)}`}
                  className="text-sm font-bold text-stone-900 hover:text-orange-600 truncate max-w-full"
                >
                  @{username}
                </Link>

                <span
                  data-testid={`suggested-followers-${cook.id}`}
                  className="text-xs text-stone-500 mt-0.5"
                >
                  {cook.followers_count ?? 0} {(cook.followers_count ?? 0) === 1 ? "follower" : "followers"}
                </span>

                {cook.bio && (
                  <p className="text-xs text-stone-600 mt-2 line-clamp-2 max-w-full">
                    {cook.bio}
                  </p>
                )}

                {cook.culinary_preferences && cook.culinary_preferences.length > 0 && (
                  <div className="flex flex-wrap justify-center gap-1 mt-2">
                    {cook.culinary_preferences.slice(0, 2).map((pref) => (
                      <span
                        key={pref}
                        className="px-2 py-0.5 text-[11px] bg-stone-100 text-stone-600 rounded-full font-medium"
                      >
                        {pref}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <div className="mt-4 w-full flex justify-center">
                <FollowButton
                  targetUserId={cook.id}
                  targetUsername={username}
                  initialFollowing={cook.is_following}
                  initialFollowersCount={cook.followers_count}
                  currentUserId={user?.id}
                  size="sm"
                  onToggle={handleFollowToggle}
                />
              </div>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
