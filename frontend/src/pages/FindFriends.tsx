import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Loader2, Search, UserCheck, Users, X } from "lucide-react";
import { useAuth } from "../context/auth";
import { errorText, searchUsers, type UserSearchResultItem } from "../services/api";
import { FollowButton } from "../components/FollowButton";

export function FindFriends() {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const urlQuery = searchParams.get("q") ?? "";

  const [query, setQuery] = useState(urlQuery);
  const [chefs, setChefs] = useState<UserSearchResultItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Sync internal query state with URL query parameter changes
  useEffect(() => {
    setQuery(urlQuery);
  }, [urlQuery]);

  // Fetch chefs matching query (or default active community members when query is empty)
  useEffect(() => {
    let active = true;
    setIsLoading(true);
    setError(null);

    const timer = setTimeout(async () => {
      try {
        const response = await searchUsers(query.trim(), 50, 0);
        if (active) {
          setChefs(response.items);
          setIsLoading(false);
        }
      } catch (err) {
        if (active) {
          setError(errorText(err));
          setIsLoading(false);
        }
      }
    }, 300);

    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [query]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setQuery(val);
    setSearchParams(val.trim() ? { q: val } : {}, { replace: true });
  };

  const handleClear = () => {
    setQuery("");
    setSearchParams({}, { replace: true });
  };

  const handleFollowToggle = (targetUserId: number, following: boolean, followersCount?: number) => {
    setChefs((prev) =>
      prev.map((chef) =>
        chef.id === targetUserId
          ? {
              ...chef,
              is_following: following,
              followers_count:
                followersCount ??
                (following ? chef.followers_count + 1 : Math.max(0, chef.followers_count - 1)),
            }
          : chef
      )
    );
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto mb-8">
        <h1 className="text-3xl font-extrabold text-stone-900 tracking-tight">
          Find Chefs &amp; Friends
        </h1>
        <p className="text-stone-600 mt-2">
          Discover passionate home cooks, explore culinary styles, and build your Simmer network.
        </p>

        {/* Directory Search Bar */}
        <div className="relative mt-6 max-w-md mx-auto flex items-center">
          <span className="absolute left-3.5 text-stone-400 pointer-events-none flex items-center">
            {isLoading ? (
              <Loader2 className="h-5 w-5 animate-spin text-orange-600" data-testid="search-spinner" />
            ) : (
              <Search className="h-5 w-5" data-testid="search-icon" />
            )}
          </span>

          <input
            type="text"
            value={query}
            onChange={handleInputChange}
            placeholder="Search by username..."
            aria-label="Search chefs by username"
            className="w-full pl-11 pr-10 py-2.5 text-base bg-white border border-stone-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-colors"
          />

          {query && (
            <button
              type="button"
              onClick={handleClear}
              aria-label="Clear chef search"
              className="absolute right-3 p-1 text-stone-400 hover:text-stone-600 rounded-full transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          )}
        </div>
      </div>

      {/* Loading Skeleton */}
      {isLoading && chefs.length === 0 && (
        <div className="flex flex-col items-center justify-center py-16 gap-3 text-stone-500">
          <Loader2 className="h-8 w-8 animate-spin text-orange-600" />
          <p className="text-sm">Finding fellow cooks...</p>
        </div>
      )}

      {/* Error Message */}
      {error && !isLoading && (
        <div className="max-w-md mx-auto p-4 bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl text-center">
          {error}
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !error && chefs.length === 0 && (
        <div className="text-center py-16 bg-white rounded-2xl border border-stone-200 p-8 max-w-md mx-auto shadow-sm">
          <div className="w-14 h-14 bg-orange-50 rounded-full flex items-center justify-center mx-auto mb-4 text-orange-600">
            <Users className="h-7 w-7" />
          </div>
          <h2 className="text-lg font-bold text-stone-900">No chefs found</h2>
          <p className="text-sm text-stone-500 mt-1">
            {query.trim()
              ? `We couldn't find any cooks matching "${query.trim()}".`
              : "No other active cooks found on the platform yet."}
          </p>
          {query.trim() && (
            <button
              type="button"
              onClick={handleClear}
              className="mt-4 px-4 py-2 text-sm bg-orange-600 text-white rounded-lg hover:bg-orange-700 font-medium transition-colors"
            >
              Clear search
            </button>
          )}
        </div>
      )}

      {/* Chefs Grid */}
      {!isLoading && !error && chefs.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {chefs.map((chef) => (
            <div
              key={chef.id}
              data-testid={`chef-card-${chef.id}`}
              className="bg-white border border-stone-200 rounded-2xl p-5 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between"
            >
              <div>
                {/* Top Row: Avatar & Follow Button */}
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3 min-w-0">
                    {chef.avatar_url ? (
                      <img
                        src={chef.avatar_url}
                        alt={chef.username}
                        className="w-14 h-14 rounded-full object-cover border-2 border-stone-100 flex-shrink-0"
                      />
                    ) : (
                      <div className="w-14 h-14 rounded-full bg-orange-100 text-orange-700 flex items-center justify-center font-bold text-lg uppercase flex-shrink-0 border-2 border-orange-200">
                        {chef.username.slice(0, 2)}
                      </div>
                    )}

                    <div className="min-w-0">
                      <h3 className="text-base font-bold text-stone-900 truncate">
                        @{chef.username}
                      </h3>
                      {chef.is_following && (
                        <span className="inline-flex items-center gap-1 text-[11px] font-medium text-orange-700 bg-orange-50 px-2 py-0.5 rounded-full mt-0.5">
                          <UserCheck className="h-3 w-3" /> Follows you / Following
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex-shrink-0">
                    <FollowButton
                      targetUserId={chef.id}
                      targetUsername={chef.username}
                      initialFollowing={chef.is_following}
                      initialFollowersCount={chef.followers_count}
                      currentUserId={user?.id}
                      size="sm"
                      onToggle={handleFollowToggle}
                    />
                  </div>
                </div>

                {/* Bio Snippet */}
                {chef.bio && (
                  <p className="text-sm text-stone-600 mt-3 line-clamp-2">
                    {chef.bio}
                  </p>
                )}

                {/* Culinary Preferences Tags */}
                {chef.culinary_preferences && chef.culinary_preferences.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-3">
                    {chef.culinary_preferences.slice(0, 4).map((pref) => (
                      <span
                        key={pref}
                        className="px-2.5 py-0.5 text-xs bg-stone-100 text-stone-700 rounded-full font-medium"
                      >
                        {pref}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Bottom Network Stats */}
              <div
                data-testid={`followers-count-${chef.id}`}
                className="flex items-center gap-4 text-xs text-stone-500 mt-4 pt-3 border-t border-stone-100"
              >
                <div>
                  <span className="font-bold text-stone-800">{chef.followers_count}</span>{" "}
                  {chef.followers_count === 1 ? "follower" : "followers"}
                </div>
                <div>
                  <span className="font-bold text-stone-800">{chef.following_count}</span> following
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
