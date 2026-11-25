// These component tests cover what readers can see and do without a live server.
// API spies keep UI failures separate from ranking failures, which backend tests cover.
// The final request test uses fetch to check the boundary that those spies bypass.
import { fireEvent, render, screen, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, expect, it, vi } from "vitest";
import { TrendingCarousel } from "../components/TrendingCarousel";
import { Home } from "../pages/Home";
import { api, type TrendingRecipe } from "../services/api";

vi.mock("../context/auth", () => ({ useAuth: () => ({ user: null }) }));
afterEach(() => vi.restoreAllMocks());

const card: TrendingRecipe = {
  id: 12, title: "Garden pasta", image_url: "/pasta.jpg", cuisine: "Italian",
  difficulty: "easy", cook_time_mins: 20, author_username: "ana",
  trending_score: 2, likes_count: 3, completed_count: 1,
};
function openCarousel() {
  return render(<MemoryRouter><TrendingCarousel /></MemoryRouter>);
}

// Protect the handoff from backend ranking to UI: sorting again here could change
// trending/fallback order. A photo-less card also checks a common incomplete-data case.
it("requests five cards and preserves server order with recipe detail links", async () => {
  vi.spyOn(api, "getTrendingRecipes").mockResolvedValue([
    card, { ...card, id: 13, title: "Soup", image_url: null },
  ]);
  openCarousel();
  const list = await screen.findByRole("list", { name: "Trending recipes" });
  expect(api.getTrendingRecipes).toHaveBeenCalledWith(5);
  const links = within(list).getAllByRole("link");
  expect(links[0]).toHaveAttribute("href", "/recipes/12");
  expect(links[1]).toHaveAttribute("href", "/recipes/13");
  expect(list).toHaveAttribute("tabindex", "0");
  expect(screen.getByText("No photo yet")).toBeInTheDocument();
});

// Resolve the request manually so this checks the pending state, not just fast success.
// An empty installation must finish loading without leaving a blank, focusable carousel.
it("shows loading then an honest empty state", async () => {
  let resolve!: (items: TrendingRecipe[]) => void;
  vi.spyOn(api, "getTrendingRecipes").mockReturnValue(new Promise((done) => { resolve = done; }));
  openCarousel();
  expect(screen.getByRole("status")).toHaveTextContent("Loading trending recipes");
  resolve([]);
  expect(await screen.findByText("No recipes to discover yet.")).toBeInTheDocument();
  expect(screen.queryByRole("list")).not.toBeInTheDocument();
});

// Network failures are temporary: retry must replace the error with usable cards.
// A success-only test would miss a stuck error message or a retry that never fetches.
it("recovers from request failure through retry", async () => {
  vi.spyOn(api, "getTrendingRecipes").mockRejectedValueOnce(new Error("Network unavailable"))
    .mockResolvedValueOnce([card]);
  openCarousel();
  expect(await screen.findByRole("alert")).toHaveTextContent("Network unavailable");
  fireEvent.click(screen.getByRole("button", { name: "Retry trending recipes" }));
  expect(await screen.findByRole("link", { name: /Garden pasta/ })).toBeInTheDocument();
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
});

// Test Home itself because a correct isolated carousel could still be omitted or
// mounted below the timeline. DOM order also determines screen-reader reading order.
it("places trending above the existing Home feed", async () => {
  vi.spyOn(api, "getTrendingRecipes").mockResolvedValue([card]);
  vi.spyOn(api, "getFeed").mockResolvedValue({ items: [], total: 0, limit: 20, offset: 0 });
  vi.spyOn(api, "searchRecipes").mockResolvedValue({ items: [], total: 0, limit: 20, offset: 0 });
  render(<MemoryRouter><Home /></MemoryRouter>);
  const heading = await screen.findByRole("heading", { name: "Trending Recipes This Week" });
  const feed = screen.getByRole("tablist", { name: "Home Feed" });
  expect(heading.compareDocumentPosition(feed) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
});

// JSDOM has no layout or native scrolling. Supply a viewport width to check that both
// controls request a page in the right direction; the browser test checks real movement.
it("scrolls in both directions using the visible list width", async () => {
  vi.spyOn(api, "getTrendingRecipes").mockResolvedValue([card]);
  openCarousel();
  const list = await screen.findByRole("list", { name: "Trending recipes" });
  Object.defineProperty(list, "clientWidth", { value: 480 });
  const scroll = vi.fn();
  list.scrollBy = scroll;
  fireEvent.click(screen.getByRole("button", { name: "Next trending recipes" }));
  expect(scroll).toHaveBeenLastCalledWith({ left: 480, behavior: "auto" });
  fireEvent.click(screen.getByRole("button", { name: "Previous trending recipes" }));
  expect(scroll).toHaveBeenLastCalledWith({ left: -480, behavior: "auto" });
});

// A saved token is deliberate: anonymous-only coverage would pass even if the client
// accidentally attached credentials. Exercise the real API helper rather than a spy.
it("uses the public list endpoint without sending a saved bearer token", async () => {
  localStorage.setItem("simmer_token", "saved-token");
  const fetchMock = vi.fn<typeof fetch>().mockResolvedValue(
    new Response(JSON.stringify([card]), { status: 200 }),
  );
  vi.stubGlobal("fetch", fetchMock);
  try {
    expect(await api.getTrendingRecipes(5)).toEqual([card]);
    const [url, options] = fetchMock.mock.calls[0];
    expect(String(url)).toContain("/api/v1/recipes/trending?limit=5");
    expect(new Headers(options?.headers).has("Authorization")).toBe(false);
  } finally {
    vi.unstubAllGlobals();
  }
});
