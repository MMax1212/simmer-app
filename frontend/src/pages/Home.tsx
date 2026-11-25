import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/auth";
import { api, errorText, type FeedResponse, type RecipeSummary } from "../services/api";
import { ErrorMessage } from "../components/ErrorMessage";
import { TrendingCarousel } from "../components/TrendingCarousel";
import { FeedCard } from "../components/FeedCard";
import { BookOpen } from "lucide-react";

// Filter pills configuration
const FILTER_PRESETS = [
  { label: "All", type: "all", value: "" },
  { label: "Italian", type: "cuisine", value: "Italian" },
  { label: "Mexican", type: "cuisine", value: "Mexican" },
  { label: "Asian", type: "cuisine", value: "Asian" },
  { label: "Breakfast", type: "meal_type", value: "breakfast" },
  { label: "Dinner", type: "meal_type", value: "dinner" },
  { label: "#quick", type: "tag", value: "quick" },
  { label: "#healthy", type: "tag", value: "healthy" },
];

export function Home() {
  const { user } = useAuth();
  const notice = (useLocation().state as { notice?: string } | null)?.notice;

  // --- US3.5 Task 3.5.5: Feed Mode State ("following" vs "global") ---
  const [feedMode, setFeedMode] = useState<"following" | "global">(() =>
    user ? "following" : "global"
  );
  const [feed, setFeed] = useState<FeedResponse | null>(null);
  const [feedLoading, setFeedLoading] = useState<boolean>(false);
  const [feedError, setFeedError] = useState<string | null>(null);

  // Sync feedMode when user auth changes
  useEffect(() => {
    setFeedMode(user ? "following" : "global");
  }, [user]);

  // Fetch timeline feed based on mode
  useEffect(() => {
    if (!user && feedMode === "following") {
      setFeed(null);
      setFeedLoading(false);
      return;
    }

    let active = true;
    setFeedLoading(true);
    setFeedError(null);

    api
      .getFeed(feedMode)
      .then((res) => {
        if (active) setFeed(res);
      })
      .catch((e) => {
        if (active) setFeedError(errorText(e));
      })
      .finally(() => {
        if (active) setFeedLoading(false);
      });

    return () => {
      active = false;
    };
  }, [feedMode, user]);

  // Recipe discovery state
  const [activeFilter, setActiveFilter] = useState({ type: "all", value: "" });
  const [recipes, setRecipes] = useState<RecipeSummary[] | null>(null);
  const [recipesLoading, setRecipesLoading] = useState(true);
  const [recipesError, setRecipesError] = useState<string | null>(null);

  // Fetch recipes whenever the selected filter changes
  useEffect(() => {
    let active = true;
    setRecipesLoading(true);
    setRecipesError(null);
    const filterParam =
      activeFilter.type === "cuisine"
        ? { cuisine: activeFilter.value }
        : activeFilter.type === "meal_type"
        ? { meal_type: activeFilter.value }
        : activeFilter.type === "tag"
        ? { tag: activeFilter.value }
        : {};
    api
      .searchRecipes(filterParam)
      .then((res) => {
        if (active) setRecipes(res.items);
      })
      .catch((e) => {
        if (active) setRecipesError(errorText(e));
      })
      .finally(() => {
        if (active) setRecipesLoading(false);
      });
    return () => {
      active = false;
    };
  }, [activeFilter]);

  return (
    <div className="flex flex-col gap-6">
      {/* Hero Banner */}
      <section className="hero">
        {notice && <p role="alert" className="error">{notice}</p>}
        <h1>{user ? `Welcome back, ${user.username}` : "Cook, share, and simmer together."}</h1>
        <p className="muted">Discover delicious recipes or share your culinary creations.</p>
        <div className="row">
          {user ? (
            <>
              <Link to="/recipes/new" className="button">Add a recipe</Link>
              <Link to="/recipes/my-recipes" className="button secondary">My Recipes</Link>
            </>
          ) : (
            <>
              <Link to="/register" className="button">Create an account</Link>
              <Link to="/login" className="button secondary">Log in</Link>
            </>
          )}
        </div>
      </section>

      {/* Discovery loads independently so a failure cannot block the timeline. */}
      <TrendingCarousel />

      {/* --- US3.5 Task 3.5.5: Tabbed Feed Navigation --- */}
      <section className="feed-section">
        <div
          role="tablist"
          aria-label="Home Feed"
          className="flex gap-6 border-b border-slate-200 mb-6"
        >
          <button
            type="button"
            role="tab"
            aria-selected={feedMode === "following"}
            className={`link-button pb-2.5 font-semibold text-base transition-colors ${
              feedMode === "following"
                ? "border-b-2 border-rose-500 text-rose-600 font-bold"
                : "text-slate-500 hover:text-slate-800"
            }`}
            onClick={() => setFeedMode("following")}
          >
            Following Feed
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={feedMode === "global"}
            className={`link-button pb-2.5 font-semibold text-base transition-colors ${
              feedMode === "global"
                ? "border-b-2 border-rose-500 text-rose-600 font-bold"
                : "text-slate-500 hover:text-slate-800"
            }`}
            onClick={() => setFeedMode("global")}
          >
            Global Community Feed
          </button>
        </div>

        {/* Unauthenticated Prompt for Following Feed */}
        {!user && feedMode === "following" && (
          <div className="card text-center py-12 flex flex-col items-center gap-3">
            <h3 className="text-lg font-semibold text-slate-800">
              Sign in to see posts from creators you follow!
            </h3>
            <p className="text-slate-500 max-w-md">
              Follow cooks and creators across the Simmer community to personalize your culinary feed.
            </p>
            <Link to="/login" className="button mt-2">
              Log in
            </Link>
          </div>
        )}

        {/* Feed Error Display */}
        {feedError && <ErrorMessage error={feedError} />}

        {/* Loading Indicator */}
        {feedLoading && !feed && <p className="muted py-6">Loading feed…</p>}

        {/* Empty State for Following Feed */}
        {user && feedMode === "following" && !feedLoading && feed && feed.items.length === 0 && (
          <div className="card text-center py-12 flex flex-col items-center gap-3">
            <h3 className="text-lg font-semibold text-slate-800">
              Your following feed is empty!
            </h3>
            <p className="text-slate-500 max-w-md">
              Follow other home cooks and creators to see their recipes and posts appear here.
            </p>
            <button
              type="button"
              className="button secondary mt-2"
              onClick={() => setFeedMode("global")}
            >
              Explore Global Community
            </button>
          </div>
        )}

        {/* Feed Post List */}
        {feed && feed.items.length > 0 && (
          <div className="feed-stream max-w-2xl mx-auto w-full">
            {feed.items.map((post) => (
              <FeedCard
                key={post.id}
                post={post}
                currentUserId={user?.id}
              />
            ))}
          </div>
        )}
      </section>

      {/* --- US2.1 (Task 2.1.4): Category Filter Pills Bar --- */}
      <section className="card">
        <div className="flex flex-col gap-2">
          <label className="text-sm font-semibold">Filter by Category & Tags:</label>
          <div className="chips" role="group" aria-label="Category and tag filter">
            {FILTER_PRESETS.map((preset) => {
              const isSelected =
                activeFilter.type === preset.type &&
                activeFilter.value.toLowerCase() === preset.value.toLowerCase();
              return (
                <button
                  key={preset.label}
                  type="button"
                  className={`chip ${isSelected ? "on" : ""}`}
                  onClick={() =>
                    setActiveFilter(
                      isSelected && preset.type !== "all"
                        ? { type: "all", value: "" }
                        : { type: preset.type, value: preset.value }
                    )
                  }
                >
                  {preset.label}
                  {isSelected && preset.type !== "all" && <span className="ml-1 font-bold">×</span>}
                </button>
              );
            })}
          </div>
        </div>
      </section>

      {/* Recipe Discovery Grid */}
      <section style={{ minHeight: "280px" }}>
        {recipesError && <ErrorMessage error={recipesError} />}
        {recipesLoading && recipes === null && <p className="muted">Loading recipes…</p>}

        {recipes && recipes.length === 0 && (
          <div
            className="flex flex-col items-center gap-3 py-12 text-center card"
            style={{ opacity: recipesLoading ? 0.6 : 1, transition: "opacity 0.15s ease" }}
          >
            <BookOpen size={48} className="text-stone-400" />
            <h3 className="text-lg font-semibold">No recipes found</h3>
            <p className="muted">No recipes match the selected category filter.</p>
            {activeFilter.type !== "all" && (
              <button
                type="button"
                className="secondary small mt-2"
                onClick={() => setActiveFilter({ type: "all", value: "" })}
              >
                Reset Filter
              </button>
            )}
          </div>
        )}

        {recipes && recipes.length > 0 && (
          <div
            className="recipe-grid"
            style={{
              opacity: recipesLoading ? 0.6 : 1,
              transition: "opacity 0.15s ease",
            }}
          >
            {recipes.map((r) => (
              <Link to={`/recipes/${r.id}`} key={r.id} className="recipe-card">
                <h3>{r.title}</h3>
                <div className="row text-xs gap-1.5 my-1">
                  {r.cuisine && <span className="chip text-xs py-0.5 px-2">{r.cuisine}</span>}
                  {r.meal_type && <span className="chip text-xs py-0.5 px-2">{r.meal_type}</span>}
                  <span className="muted">· {r.difficulty}</span>
                </div>
                {r.tags && r.tags.length > 0 && (
                  <div className="row gap-1 my-1">
                    {r.tags.map((t) => (
                      <span key={t} className="chip on text-xs py-0.5 px-2 font-semibold">
                        {t}
                      </span>
                    ))}
                  </div>
                )}
                <p className="small muted">
                  By {r.author_username} · {r.cook_time_mins} min cook
                </p>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
