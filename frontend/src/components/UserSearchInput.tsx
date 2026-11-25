import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Loader2, Search, X } from "lucide-react";
import { errorText, searchUsers, type UserSearchResultItem } from "../services/api";
import { FollowButton } from "./FollowButton";

export interface UserSearchInputProps {
  placeholder?: string;
  onSelectUser?: (user: UserSearchResultItem) => void;
  currentUserId?: number;
  className?: string;
  autoFocus?: boolean;
}

export function UserSearchInput({
  placeholder = "Search chefs & friends...",
  onSelectUser,
  currentUserId,
  className = "",
  autoFocus = false,
}: UserSearchInputProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<UserSearchResultItem[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeIndex, setActiveIndex] = useState(-1);

  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  // 300ms Debounce Effect
  useEffect(() => {
    const trimmed = query.trim();
    if (!trimmed) {
      setResults([]);
      setIsOpen(false);
      setIsLoading(false);
      setError(null);
      setActiveIndex(-1);
      return;
    }

    setIsLoading(true);
    setError(null);
    setIsOpen(true);

    let active = true;
    const timer = setTimeout(async () => {
      try {
        const response = await searchUsers(trimmed, 10, 0);
        if (active) {
          setResults(response.items);
          setIsLoading(false);
          setActiveIndex(-1);
        }
      } catch (err) {
        if (active) {
          setError(errorText(err));
          setResults([]);
          setIsLoading(false);
        }
      }
    }, 300);

    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [query]);

  // Click Outside to Dismiss
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setActiveIndex(-1);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const handleSelect = (user: UserSearchResultItem) => {
    setIsOpen(false);
    setActiveIndex(-1);
    if (onSelectUser) {
      onSelectUser(user);
    } else {
      // Default action: navigate to friends directory with search query
      navigate(`/friends?q=${encodeURIComponent(user.username)}`);
    }
  };

  const handleClear = () => {
    setQuery("");
    setResults([]);
    setIsOpen(false);
    setActiveIndex(-1);
    setError(null);
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen && (e.key === "ArrowDown" || e.key === "ArrowUp") && results.length > 0) {
      setIsOpen(true);
      return;
    }

    if (!isOpen) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIndex((prev) => (prev + 1 < results.length ? prev + 1 : 0));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex((prev) => (prev > 0 ? prev - 1 : results.length - 1));
    } else if (e.key === "Enter") {
      if (activeIndex >= 0 && activeIndex < results.length) {
        e.preventDefault();
        handleSelect(results[activeIndex]);
      }
    } else if (e.key === "Escape") {
      e.preventDefault();
      setIsOpen(false);
      setActiveIndex(-1);
    }
  };

  const handleFollowToggle = (targetUserId: number, following: boolean, followersCount?: number) => {
    setResults((prev) =>
      prev.map((item) =>
        item.id === targetUserId
          ? {
              ...item,
              is_following: following,
              followers_count: followersCount ?? (following ? item.followers_count + 1 : Math.max(0, item.followers_count - 1)),
            }
          : item
      )
    );
  };

  return (
    <div ref={containerRef} className={`relative w-full max-w-md ${className}`}>
      {/* Search Input Box */}
      <div className="relative flex items-center">
        <span className="absolute left-3 text-stone-400 pointer-events-none flex items-center">
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin text-orange-600" data-testid="search-spinner" />
          ) : (
            <Search className="h-4 w-4" data-testid="search-icon" />
          )}
        </span>

        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => {
            if (query.trim() && (results.length > 0 || isLoading)) {
              setIsOpen(true);
            }
          }}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          autoFocus={autoFocus}
          role="combobox"
          aria-expanded={isOpen}
          aria-autocomplete="list"
          aria-controls="user-search-listbox"
          aria-activedescendant={activeIndex >= 0 ? `user-search-item-${activeIndex}` : undefined}
          className="w-full pl-9 pr-9 py-2 text-sm bg-white border border-stone-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-colors"
        />

        {query && (
          <button
            type="button"
            onClick={handleClear}
            aria-label="Clear search"
            className="absolute right-2.5 p-1 text-stone-400 hover:text-stone-600 rounded-full transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Live Dropdown Results */}
      {isOpen && (
        <div
          id="user-search-listbox"
          role="listbox"
          className="absolute z-50 left-0 right-0 mt-1.5 max-h-80 overflow-y-auto bg-white border border-stone-200 rounded-xl shadow-lg divide-y divide-stone-100"
        >
          {isLoading && results.length === 0 && (
            <div className="p-4 text-center text-sm text-stone-500 flex items-center justify-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin text-orange-600" />
              <span>Searching chefs...</span>
            </div>
          )}

          {error && !isLoading && (
            <div className="p-3 text-center text-sm text-red-600 bg-red-50">{error}</div>
          )}

          {!isLoading && !error && results.length === 0 && query.trim() && (
            <div className="p-4 text-center text-sm text-stone-500">
              No cooks found matching &ldquo;{query.trim()}&rdquo;
            </div>
          )}

          {results.map((user, index) => {
            const isHighlighted = index === activeIndex;
            return (
              <div
                key={user.id}
                id={`user-search-item-${index}`}
                role="option"
                aria-selected={isHighlighted}
                onMouseEnter={() => setActiveIndex(index)}
                onClick={() => handleSelect(user)}
                className={`flex items-center justify-between px-3.5 py-2.5 cursor-pointer transition-colors ${
                  isHighlighted ? "bg-orange-50" : "hover:bg-stone-50"
                }`}
              >
                {/* User Info Left */}
                <div className="flex items-center gap-3 min-w-0 pr-2">
                  {user.avatar_url ? (
                    <img
                      src={user.avatar_url}
                      alt={user.username}
                      className="w-9 h-9 rounded-full object-cover flex-shrink-0 border border-stone-200"
                    />
                  ) : (
                    <div className="w-9 h-9 rounded-full bg-orange-100 text-orange-700 flex items-center justify-center font-bold text-xs uppercase flex-shrink-0">
                      {user.username.slice(0, 2)}
                    </div>
                  )}

                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-stone-900 truncate">
                      @{user.username}
                    </p>
                    <p className="text-xs text-stone-500 truncate">
                      {user.followers_count} {user.followers_count === 1 ? "follower" : "followers"}
                      {user.bio ? ` • ${user.bio}` : ""}
                    </p>
                  </div>
                </div>

                {/* Inline Follow Button */}
                <div className="flex-shrink-0" onClick={(e) => e.stopPropagation()}>
                  <FollowButton
                    targetUserId={user.id}
                    targetUsername={user.username}
                    initialFollowing={user.is_following}
                    initialFollowersCount={user.followers_count}
                    currentUserId={currentUserId}
                    size="sm"
                    onToggle={handleFollowToggle}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
