// These tests focus on UI/session boundaries; backend tests own preference matching.
// Deferred responses deliberately model account changes while a request is in flight.
import { act, fireEvent, render, screen, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, expect, it, vi } from "vitest";
import { RecommendedRecipes } from "../components/RecommendedRecipes";
import { AuthContext, type AuthState } from "../context/auth";
import { api, type TrendingRecipe } from "../services/api";
import { user } from "./fixtures";

const card: TrendingRecipe = {
  id: 12, title: "Garden pasta", image_url: null, cuisine: "Italian",
  difficulty: "easy", cook_time_mins: 20, author_username: "ana",
  trending_score: 2, likes_count: 3, completed_count: 1,
};
afterEach(() => { vi.restoreAllMocks(); vi.unstubAllGlobals(); });

function tree(currentUser: AuthState["user"], loading = false) {
  const auth: AuthState = {
    user: currentUser, loading, login: vi.fn(), register: vi.fn(),
    logout: vi.fn(), setUser: vi.fn(),
  };
  return <MemoryRouter><AuthContext.Provider value={auth}>
    <RecommendedRecipes />
  </AuthContext.Provider></MemoryRouter>;
}

// Neither an anonymous visitor nor an unresolved session should call the private API.
it("does not fetch or show recommendations without a resolved signed-in user", () => {
  const request = vi.spyOn(api, "getRecommendedRecipes");
  const view = render(tree(null));
  expect(request).not.toHaveBeenCalled();
  expect(screen.queryByRole("region")).not.toBeInTheDocument();
  view.rerender(tree(user, true));
  expect(request).not.toHaveBeenCalled();
});

// Keep server ordering: client-side reranking could undo preference relevance or fallback.
it("loads authenticated cards in server order with detail links", async () => {
  vi.spyOn(api, "getRecommendedRecipes").mockResolvedValue([
    card, { ...card, id: 13, title: "Soup" },
  ]);
  render(tree(user));
  const links = within(await screen.findByRole("list")).getAllByRole("link");
  expect(api.getRecommendedRecipes).toHaveBeenCalledWith(5);
  expect(links.map((link) => link.getAttribute("href"))).toEqual(["/recipes/12", "/recipes/13"]);
});

// A deferred result makes the loading state observable and prevents a fast mock hiding it.
it("shows pending then empty states without claiming a preference match", async () => {
  let resolve!: (cards: TrendingRecipe[]) => void;
  vi.spyOn(api, "getRecommendedRecipes").mockReturnValue(
    new Promise((done) => { resolve = done; }),
  );
  render(tree({ ...user, culinary_preferences: ["Italian"] }));
  expect(screen.getByRole("status")).toHaveTextContent("Loading recommendations");
  await act(async () => resolve([]));
  expect(screen.getByText("No recommendations found for your preferences.")).toBeInTheDocument();
  expect(screen.queryByRole("list")).not.toBeInTheDocument();
});

// Recovery matters independently of initial success: stale errors must not mask new cards.
it("retries a failed request", async () => {
  vi.spyOn(api, "getRecommendedRecipes").mockRejectedValueOnce(new Error("Offline"))
    .mockResolvedValueOnce([card]);
  render(tree(user));
  expect(await screen.findByRole("alert")).toHaveTextContent("Offline");
  fireEvent.click(screen.getByRole("button", { name: "Retry recommendations" }));
  const recipeLink = await screen.findByRole("link", { name: /Garden pasta/ });
  expect(recipeLink).toHaveAttribute("href", "/recipes/12");
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
});

// This is a privacy regression: a late result must not repopulate a different session.
it("ignores an old account response and clears cards on logout", async () => {
  let oldResult!: (cards: TrendingRecipe[]) => void;
  vi.spyOn(api, "getRecommendedRecipes")
    .mockReturnValueOnce(new Promise((done) => { oldResult = done; }))
    .mockResolvedValueOnce([{ ...card, id: 20, title: "Other user's soup" }]);
  const view = render(tree(user));
  view.rerender(tree({ ...user, id: 99 }));
  const recipeLink = await screen.findByRole("link", { name: /Other user/ });
  expect(recipeLink).toHaveAttribute("href", "/recipes/20");
  await act(async () => oldResult([card]));
  expect(screen.queryByText("Garden pasta")).not.toBeInTheDocument();
  view.rerender(tree(null));
  expect(screen.queryByRole("link")).not.toBeInTheDocument();
});

// Same account, new preferences: old suggestions should disappear immediately, not flash.
it("refreshes recommendations when saved preferences change", async () => {
  vi.spyOn(api, "getRecommendedRecipes").mockResolvedValueOnce([card])
    .mockResolvedValueOnce([{ ...card, id: 21, title: "New preference result" }]);
  const view = render(tree(user));
  await screen.findByText("Garden pasta");
  view.rerender(tree({ ...user, culinary_preferences: ["Mexican"] }));
  expect(screen.queryByText("Garden pasta")).not.toBeInTheDocument();
  expect(await screen.findByText("New preference result")).toBeInTheDocument();
  expect(api.getRecommendedRecipes).toHaveBeenCalledTimes(2);
});

// Exercise the real helper: component spies cannot prove bearer-token handling.
it("sends the saved bearer token to the recommendations endpoint", async () => {
  localStorage.setItem("simmer_token", "saved-token");
  const request = vi.fn<typeof fetch>().mockResolvedValue(new Response(JSON.stringify([card])));
  vi.stubGlobal("fetch", request);
  expect(await api.getRecommendedRecipes(5)).toEqual([card]);
  const [url, options] = request.mock.calls[0];
  expect(String(url)).toContain("/api/v1/recipes/recommended?limit=5");
  expect(new Headers(options?.headers).get("Authorization")).toBe("Bearer saved-token");
});

// New users should understand why suggestions appear before selecting preferences.
// These are server fallback results, not an excuse to label arbitrary recipes a match.
it("labels empty-preference suggestions and links to profile setup", async () => {
  vi.spyOn(api, "getRecommendedRecipes").mockResolvedValue([card]);
  render(tree({ ...user, culinary_preferences: ["# "] }));
  expect(await screen.findByText("Community picks")).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "Choose your preferences" }))
    .toHaveAttribute("href", "/profile");
  expect(screen.getByRole("link", { name: /Garden pasta/ })).toBeInTheDocument();
});

// An empty catalog and an unsuccessful preference match need different guidance.
it("gives a new user an actionable empty-community state", async () => {
  vi.spyOn(api, "getRecommendedRecipes").mockResolvedValue([]);
  render(tree(user));
  expect(await screen.findByText("The community is just getting started."))
    .toBeInTheDocument();
  expect(screen.getByRole("link", { name: "Share a recipe" }))
    .toHaveAttribute("href", "/recipes/new");
  expect(screen.queryByText("No recommendations found for your preferences."))
    .not.toBeInTheDocument();
});

it("offers browsing for genuine nonmatches without claiming community fallback", async () => {
  vi.spyOn(api, "getRecommendedRecipes").mockResolvedValue([]);
  render(tree({ ...user, culinary_preferences: ["Italian"] }));
  await screen.findByText("No recommendations found for your preferences.");
  expect(screen.getByRole("link", { name: "Browse all recipes" }))
    .toHaveAttribute("href", "/recipes");
  expect(screen.queryByText("Community picks")).not.toBeInTheDocument();
});

// Service outages must stay distinguishable from a successful cold-start response.
it("does not show cold-start guidance for a failed request", async () => {
  vi.spyOn(api, "getRecommendedRecipes").mockRejectedValue(new Error("Offline"));
  render(tree(user));
  await screen.findByRole("alert");
  expect(screen.queryByText("Community picks")).not.toBeInTheDocument();
  expect(screen.queryByText("The community is just getting started."))
    .not.toBeInTheDocument();
});
