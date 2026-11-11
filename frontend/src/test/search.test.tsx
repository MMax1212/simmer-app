import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "../App";
import type { RecipeSearchResult } from "../services/api";
import userEvent from "@testing-library/user-event";

const respond = (data: unknown, status = 200) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
const fetchMock = vi.fn<typeof fetch>();
beforeEach(() => {
  vi.stubGlobal("fetch", fetchMock);
  fetchMock.mockReset();
});
function open(path: string) {
  window.history.replaceState(null, "", path);
  render(<App />);
}
const mockSearchResult: RecipeSearchResult = {
  total: 1,
  limit: 20,
  offset: 0,
  items: [
    {
      id: 1,
      title: "Tomato Pasta",
      author_username: "ana",
      cuisine: "Italian",
      meal_type: "dinner",
      difficulty: "easy",
      cook_time_mins: 20,
      image_url: null,
    },
  ],
};
describe("US2.2: Recipe Search & Discovery", () => {
  // --- US2.2: Task 2.2: Initial Discovery Screen & Recipe Cards ---
  it("renders search input and recipe cards at /recipes", async () => {
    fetchMock.mockResolvedValue(respond(mockSearchResult));
    open("/recipes");
    // Expect the header and search input to exist
    expect(await screen.findByRole("heading", { name: "Explore Recipes" })).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Search recipes by title or ingredient...")).toBeInTheDocument();
    // Expect the recipe card from the search results to be rendered
    expect(await screen.findByText("Tomato Pasta")).toBeInTheDocument();
  });

  // --- US2.2: Task 2.3: Category Pill Filtering ---
  it("filters recipes when clicking a category pill", async () => {
    const actor = userEvent.setup();
    fetchMock.mockResolvedValue(respond(mockSearchResult));
    open("/recipes");
    // Expect category filter pills to be present
    const italianPill = await screen.findByRole("button", { name: "Italian" });
    expect(italianPill).toBeInTheDocument();
        // Click the "Italian" category pill
    await actor.click(italianPill);

    // Wait for the 300ms debounce timer to fire the request
    await waitFor(() => {
      expect(fetchMock.mock.calls.some(([url]) => String(url).includes("cuisine=Italian"))).toBe(true);
    });

    // Clicking "All" resets the cuisine filter
    const allPill = screen.getByRole("button", { name: "All" });
    await actor.click(allPill);

    // Wait for the reset request without cuisine=Italian
    await waitFor(() => {
      expect(fetchMock.mock.calls.some(([url]) => !String(url).includes("cuisine=Italian"))).toBe(true);
        });
    });
  // --- US2.2: Task 2.4: Empty State & Reset Filters ---
  it("displays empty state when no recipes match and resets on button click", async () => {
    const actor = userEvent.setup();
    // First return 0 results (empty state)
    const emptyResult: RecipeSearchResult = { total: 0, limit: 20, offset: 0, items: [] };
    fetchMock.mockImplementation(async (url) => {
      const urlStr = String(url);
      if (urlStr.includes("q=nonexistent")) return respond(emptyResult);
      return respond(mockSearchResult);
    });
    open("/recipes");
    // Type a query that yields no matches
    const input = screen.getByPlaceholderText("Search recipes by title or ingredient...");
    await actor.type(input, "nonexistent");
    // Expect the empty state message and Reset button to appear
    expect(await screen.findByText("No recipes match your search criteria.")).toBeInTheDocument();
    const resetButton = screen.getByRole("button", { name: "Reset all filters" });
    expect(resetButton).toBeInTheDocument();
    // Click Reset all filters
    await actor.click(resetButton);
    // The search input should be cleared and recipes restored
    expect(input).toHaveValue("");
    expect(await screen.findByText("Tomato Pasta")).toBeInTheDocument();
  });
});

