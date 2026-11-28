import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as AuthContext from "../context/auth";
import { RecipesPage } from "../pages/RecipesPage";
import { api, type RecipeSearchResult, type User } from "../services/api";

const mockUser: User = {
  id: 1,
  username: "chef_ana",
  email: "ana@example.com",
  role: "user",
  is_active: true,
  bio: null,
  avatar_url: null,
  culinary_preferences: [],
  created_at: "2026-10-12",
};

const mockMultiFacetResult: RecipeSearchResult = {
  total: 1,
  limit: 20,
  offset: 0,
  items: [
    {
      id: 50,
      title: "Gluten-Free Vegan Thai Curry",
      author_username: "chef_ana",
      cuisine: "Asian",
      meal_type: "dinner",
      difficulty: "easy",
      cook_time_mins: 20,
      image_url: null,
      tags: ["#vegan", "#gluten-free", "#under-30-mins", "#comfort-food"],
    },
  ],
};

beforeEach(() => {
  vi.spyOn(AuthContext, "useAuth").mockReturnValue({
    user: mockUser,
    loading: false,
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
    setUser: vi.fn(),
  });
});

describe("US4.4.6: Multi-Facet Combinatorial & Integration Suite", () => {
  // --- AC6: Full Multi-Facet Search Lifecycle on RecipesPage ---
  it("US4.4.6: simultaneously combines text query, cuisine pill, multi-dietary chips, occasion, and max time (AC6)", async () => {
    const searchSpy = vi.spyOn(api, "searchRecipes").mockResolvedValue(mockMultiFacetResult);
    const actor = userEvent.setup();

    render(
      <MemoryRouter initialEntries={["/recipes"]}>
        <RecipesPage />
      </MemoryRouter>
    );

    // Initial search
    await waitFor(() => expect(searchSpy).toHaveBeenCalled());

    // 1. Enter text query
    const searchInput = screen.getByPlaceholderText(/search recipes by title or ingredient/i);
    await actor.type(searchInput, "curry");

    // 2. Select category pill
    const asianPill = screen.getByRole("button", { name: "Asian" });
    await actor.click(asianPill);

    // 3. Open Filter Drawer
    const filtersBtn = screen.getByRole("button", { name: /filters/i });
    await actor.click(filtersBtn);

    const drawer = screen.getByRole("dialog", { name: /filter recipes/i });
    expect(drawer).toBeInTheDocument();

    // 4. Multi-select dietary chips in drawer
    const veganChip = within(drawer).getByRole("button", { name: "Vegan" });
    const gfChip = within(drawer).getByRole("button", { name: "Gluten-Free" });
    await actor.click(veganChip);
    await actor.click(gfChip);

    // 5. Select occasion badge in drawer
    const under30Chip = within(drawer).getByRole("button", { name: "Under 30 Mins" });
    await actor.click(under30Chip);

    // 6. Select max cooking time in drawer
    const timeBtn = within(drawer).getByRole("button", { name: "≤ 30 mins" });
    await actor.click(timeBtn);

    // Assert API dispatched with all facets
    await waitFor(
      () => {
        expect(searchSpy).toHaveBeenCalledWith(
          expect.objectContaining({
            q: "curry",
            cuisine: "Asian",
            dietary: "vegan,gluten-free",
            occasion: "under-30-mins",
            max_time: 30,
          })
        );
      },
      { timeout: 1500 }
    );

    // Active filters badge reflects non-category facets: 2 dietary + 1 occasion + 1 max time = 4
    expect(screen.getByRole("button", { name: /filters \(4\)/i })).toBeInTheDocument();
  });

  // --- AC7: Full Reset Lifecycle ---
  it("US4.4.6: resets all active facets via drawer Clear All and empty state recovery (AC7)", async () => {
    const searchSpy = vi.spyOn(api, "searchRecipes").mockResolvedValue(mockMultiFacetResult);
    const actor = userEvent.setup();

    render(
      <MemoryRouter initialEntries={["/recipes?dietary=vegan&occasion=quick-dinner&max_time=30"]}>
        <RecipesPage />
      </MemoryRouter>
    );

    // Filter button shows 3 active filters from URL
    expect(await screen.findByRole("button", { name: /filters \(3\)/i })).toBeInTheDocument();

    // Open drawer
    await actor.click(screen.getByRole("button", { name: /filters \(3\)/i }));

    // Click Clear all
    const clearBtn = screen.getByRole("button", { name: /clear all/i });
    await actor.click(clearBtn);

    // Drawer filters should be cleared
    await waitFor(() => {
      expect(searchSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          dietary: undefined,
          occasion: undefined,
          max_time: undefined,
        })
      );
    });

    // Badge returns to bare "Filters" without count
    expect(screen.getByRole("button", { name: /^filters$/i })).toBeInTheDocument();
  });

  // --- AC6 & AC7: Keyboard accessibility & Escape key lifecycle ---
  it("US4.4.6: drawer dismisses gracefully with Escape key without losing active filter selections (AC6)", async () => {
    vi.spyOn(api, "searchRecipes").mockResolvedValue(mockMultiFacetResult);
    const actor = userEvent.setup();

    render(
      <MemoryRouter initialEntries={["/recipes"]}>
        <RecipesPage />
      </MemoryRouter>
    );

    const filtersBtn = screen.getByRole("button", { name: /filters/i });
    await actor.click(filtersBtn);

    const drawer = screen.getByRole("dialog", { name: /filter recipes/i });
    expect(drawer).toBeInTheDocument();

    // Select Vegan
    await actor.click(within(drawer).getByRole("button", { name: "Vegan" }));

    // Press Escape
    await actor.keyboard("{Escape}");

    // Drawer is closed
    expect(screen.queryByRole("dialog")).toBeNull();

    // Selection was retained (Filters (1))
    expect(screen.getByRole("button", { name: /filters \(1\)/i })).toBeInTheDocument();
  });
});
