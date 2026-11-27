import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as AuthContext from "../context/auth";
import { Home } from "../pages/Home";
import { RecipesPage } from "../pages/RecipesPage";
import {
  QuickFilterPresets,
  type QuickFilterPreset,
} from "../components/QuickFilterPresets";
import { api, type RecipeSearchResult, type User } from "../services/api";

const respond = (data: unknown, status = 200) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });

const fetchMock = vi.fn<typeof fetch>();

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

const mockRecipeResults: RecipeSearchResult = {
  total: 2,
  limit: 20,
  offset: 0,
  items: [
    {
      id: 101,
      title: "Vegan Avocado Bowl",
      author_username: "chef_ana",
      cuisine: "Mexican",
      meal_type: "lunch",
      difficulty: "easy",
      cook_time_mins: 15,
      image_url: null,
      tags: ["#vegan", "#quick-dinner", "#gluten-free"],
    },
    {
      id: 102,
      title: "Garlic Butter Steak",
      author_username: "chef_john",
      cuisine: "American",
      meal_type: "dinner",
      difficulty: "medium",
      cook_time_mins: 25,
      image_url: null,
      tags: ["#keto", "#date-night"],
    },
  ],
};

beforeEach(() => {
  vi.stubGlobal("fetch", fetchMock);
  fetchMock.mockReset();
  vi.spyOn(AuthContext, "useAuth").mockReturnValue({
    user: mockUser,
    loading: false,
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
    setUser: vi.fn(),
  });
});

describe("US4.4.5: Quick-Filter Preset Cards on Home Explore Page", () => {
  // --- AC1: Renders Curated Preset Cards ---
  it("US4.4.5: QuickFilterPresets renders all 6 curated preset cards with titles and descriptions (AC1)", () => {
    render(<QuickFilterPresets selectedPresetId={null} onSelectPreset={vi.fn()} />);

    expect(screen.getByText("Under 30 Mins")).toBeInTheDocument();
    expect(screen.getByText("Plant-Based")).toBeInTheDocument();
    expect(screen.getByText("Date Night Dinner")).toBeInTheDocument();
    expect(screen.getByText("Meal Prep")).toBeInTheDocument();
    expect(screen.getByText("Comfort Food")).toBeInTheDocument();
    expect(screen.getByText("Low-Carb & Keto")).toBeInTheDocument();

    expect(screen.getAllByRole("button").length).toBe(6);
  });

  // --- AC2: Clicking Preset Triggers onSelectPreset with Filter Config ---
  it("US4.4.5: clicking a preset card calls onSelectPreset with preset filters (AC2)", async () => {
    const actor = userEvent.setup();
    const handleSelect = vi.fn();

    render(<QuickFilterPresets selectedPresetId={null} onSelectPreset={handleSelect} />);

    const under30Btn = screen.getByRole("button", { name: /under 30 mins/i });
    await actor.click(under30Btn);

    expect(handleSelect).toHaveBeenCalledTimes(1);
    const selected: QuickFilterPreset = handleSelect.mock.calls[0][0];
    expect(selected.id).toBe("under-30-mins");
    expect(selected.filters.max_time).toBe(30);
  });

  // --- AC3: Clicking Active Preset Toggles Off ---
  it("US4.4.5: clicking an active preset card toggles it off and calls onSelectPreset(null) (AC3)", async () => {
    const actor = userEvent.setup();
    const handleSelect = vi.fn();

    render(
      <QuickFilterPresets selectedPresetId="plant-based" onSelectPreset={handleSelect} />
    );

    const plantBasedBtn = screen.getByRole("button", { name: /plant-based/i });
    expect(plantBasedBtn).toHaveAttribute("aria-pressed", "true");

    await actor.click(plantBasedBtn);
    expect(handleSelect).toHaveBeenCalledWith(null);
  });

  // --- AC4: Home Page Integration and Filtering ---
  it("US4.4.5: Home explore page mounts preset cards and queries searchRecipes with preset filters (AC4)", async () => {
    const searchSpy = vi.spyOn(api, "searchRecipes").mockResolvedValue(mockRecipeResults);

    fetchMock.mockImplementation(async (url) => {
      if (String(url).includes("/feed")) {
        return respond({ items: [], next_cursor: null });
      }
      return respond([]);
    });

    const actor = userEvent.setup();
    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>
    );

    // Initial load calls searchRecipes without preset
    await waitFor(() => expect(searchSpy).toHaveBeenCalled());

    const dateNightBtn = await screen.findByRole("button", { name: /date night dinner/i });
    await actor.click(dateNightBtn);

    // Should call searchRecipes with occasion="date-night"
    await waitFor(() => {
      expect(searchSpy).toHaveBeenCalledWith(
        expect.objectContaining({ occasion: "date-night" })
      );
    });
  });

  // --- AC5: Home Recipe Grid Uses RecipeCard with Dietary & Occasion Badges ---
  it("US4.4.5: Home recipe grid displays RecipeCard with dietary badge pills and occasion icons (AC5)", async () => {
    vi.spyOn(api, "searchRecipes").mockResolvedValue(mockRecipeResults);
    fetchMock.mockImplementation(async (url) => {
      if (String(url).includes("/feed")) return respond({ items: [], next_cursor: null });
      return respond([]);
    });

    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>
    );

    // Should render RecipeCard elements with dietary badge pills
    expect(await screen.findByRole("heading", { name: "Vegan Avocado Bowl" })).toBeInTheDocument();
    expect(screen.getByText("Vegan")).toBeInTheDocument();
    expect(screen.getByText("Gluten-Free")).toBeInTheDocument();

    expect(screen.getByRole("heading", { name: "Garlic Butter Steak" })).toBeInTheDocument();
    expect(screen.getByText("Keto")).toBeInTheDocument();
    expect(screen.getByText("Date Night")).toBeInTheDocument();
  });

  // --- AC6: RecipesPage Initializes Filters from URL SearchParams ---
  it("US4.4.5: RecipesPage initializes filter state and searches from URL searchParams (AC6)", async () => {
    const searchSpy = vi.spyOn(api, "searchRecipes").mockResolvedValue(mockRecipeResults);

    render(
      <MemoryRouter initialEntries={["/recipes?dietary=vegan&occasion=quick-dinner&max_time=30"]}>
        <RecipesPage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(searchSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          dietary: "vegan",
          occasion: "quick-dinner",
          max_time: 30,
        })
      );
    });

    // Filters button should indicate active filters from URL (3 active filters)
    expect(screen.getByRole("button", { name: /filters \(3\)/i })).toBeInTheDocument();
  });
});
