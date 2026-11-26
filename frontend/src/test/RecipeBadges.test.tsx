import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { RecipeBadges } from "../components/RecipeBadges";
import { RecipeCard } from "../components/RecipeCard";
import { AuthContext, type AuthState } from "../context/auth";
import { RecipeDetail } from "../pages/RecipeDetail";
import { api, type RecipeSummary } from "../services/api";

const mockAuth: AuthState = {
  user: null,
  loading: false,
  login: vi.fn(),
  register: vi.fn(),
  logout: vi.fn(),
  setUser: vi.fn(),
};

describe("US4.4.4: Dietary & Occasion Badges", () => {
  // --- AC1: Curated Dietary Badge Rendering ---
  it("US4.4.4: renders curated dietary tags with dietary badge styling and formatted label (AC1)", () => {
    render(<RecipeBadges tags={["#vegan", "#gluten-free", "#dairy-free"]} />);

    const veganBadge = screen.getByText("Vegan");
    expect(veganBadge).toBeInTheDocument();
    expect(veganBadge.closest(".dietary-badge")).toHaveClass("badge-dietary");

    const gfBadge = screen.getByText("Gluten-Free");
    expect(gfBadge).toBeInTheDocument();
    expect(gfBadge.closest(".dietary-badge")).toHaveClass("badge-dietary");

    const dfBadge = screen.getByText("Dairy-Free");
    expect(dfBadge).toBeInTheDocument();
    expect(dfBadge.closest(".dietary-badge")).toHaveClass("badge-dietary");
  });

  // --- AC2: Occasion Badge Rendering with Icons ---
  it("US4.4.4: renders occasion tags with appropriate icons and formatted label (AC2)", () => {
    const { container } = render(
      <RecipeBadges tags={["#quick-dinner", "#date-night", "#meal-prep"]} />
    );

    const quickBadge = screen.getByText("Quick Dinner");
    expect(quickBadge).toBeInTheDocument();
    expect(quickBadge.closest(".dietary-badge")).toHaveClass("badge-occasion");

    const dateNightBadge = screen.getByText("Date Night");
    expect(dateNightBadge).toBeInTheDocument();
    expect(dateNightBadge.closest(".dietary-badge")).toHaveClass("badge-occasion");

    const mealPrepBadge = screen.getByText("Meal Prep");
    expect(mealPrepBadge).toBeInTheDocument();
    expect(mealPrepBadge.closest(".dietary-badge")).toHaveClass("badge-occasion");

    // Icons rendered (svg elements inside badge-occasion)
    const svgs = container.querySelectorAll(".badge-occasion svg");
    expect(svgs.length).toBeGreaterThanOrEqual(3);
  });

  // --- AC1 & AC2: Non-curated General Tags ---
  it("US4.4.4: renders general non-curated tags as standard tag chips (AC1, AC2)", () => {
    render(<RecipeBadges tags={["#spicy", "#dessert"]} />);

    const spicy = screen.getByText("#spicy");
    expect(spicy).toBeInTheDocument();
    expect(spicy.closest(".dietary-badge")).toHaveClass("badge-general");

    const dessert = screen.getByText("#dessert");
    expect(dessert).toBeInTheDocument();
    expect(dessert.closest(".dietary-badge")).toHaveClass("badge-general");
  });

  // --- AC6: Accessible Labels & ARIA Grouping ---
  it("US4.4.4: provides accessible aria-labels and semantic grouping for screen readers (AC6)", () => {
    render(
      <RecipeBadges
        tags={["#vegan", "#quick-dinner", "#spicy"]}
        ariaLabel="Recipe dietary and occasion badges"
      />
    );

    const group = screen.getByRole("group", { name: "Recipe dietary and occasion badges" });
    expect(group).toBeInTheDocument();

    const vegan = screen.getByLabelText("Dietary: Vegan");
    expect(vegan).toBeInTheDocument();

    const quick = screen.getByLabelText("Occasion: Quick Dinner");
    expect(quick).toBeInTheDocument();
  });

  // --- AC4: Graceful Handling of Empty or Undefined Tags ---
  it("US4.4.4: returns null or empty when tags list is empty or undefined (AC4)", () => {
    const { container: c1 } = render(<RecipeBadges tags={[]} />);
    expect(c1.firstChild).toBeNull();

    const { container: c2 } = render(<RecipeBadges />);
    expect(c2.firstChild).toBeNull();
  });

  // --- AC3: RecipeCard displays dietary & occasion badge pills ---
  it("US4.4.4: RecipeCard renders title, metadata, and dietary & occasion badge pills (AC3)", () => {
    const mockRecipe: RecipeSummary = {
      id: 42,
      title: "Mediterranean Grain Bowl",
      author_username: "chef_marina",
      cuisine: "Mediterranean",
      meal_type: "lunch",
      difficulty: "easy",
      cook_time_mins: 25,
      image_url: null,
      tags: ["#vegan", "#gluten-free", "#under-30-mins"],
    };

    render(
      <MemoryRouter>
        <RecipeCard recipe={mockRecipe} />
      </MemoryRouter>
    );

    expect(screen.getByRole("heading", { name: "Mediterranean Grain Bowl" })).toBeInTheDocument();
    expect(screen.getByText(/By chef_marina/)).toBeInTheDocument();
    expect(screen.getByText("Vegan")).toBeInTheDocument();
    expect(screen.getByText("Gluten-Free")).toBeInTheDocument();
    expect(screen.getByText("Under 30 Mins")).toBeInTheDocument();
  });

  // --- AC4: RecipeCard without tags renders cleanly without badge wrapper ---
  it("US4.4.4: RecipeCard renders cleanly without badge wrapper when recipe has no tags (AC4)", () => {
    const mockRecipe: RecipeSummary = {
      id: 43,
      title: "Plain Sourdough Bread",
      author_username: "baker_john",
      cuisine: "French",
      meal_type: "breakfast",
      difficulty: "medium",
      cook_time_mins: 45,
      image_url: null,
      tags: [],
    };

    const { container } = render(
      <MemoryRouter>
        <RecipeCard recipe={mockRecipe} />
      </MemoryRouter>
    );

    expect(screen.getByRole("heading", { name: "Plain Sourdough Bread" })).toBeInTheDocument();
    expect(container.querySelector(".dietary-badges")).toBeNull();
  });

  // --- AC5: RecipeDetail renders enriched dietary badges and occasion tags ---
  it("US4.4.4: RecipeDetail renders enriched dietary badges and occasion tags (AC5)", async () => {
    vi.spyOn(api, "getRecipe").mockResolvedValue({
      id: 10,
      author_id: 1,
      author_username: "ana",
      title: "Keto Cauliflower Rice",
      description: "Quick dinner recipe",
      cuisine: "American",
      meal_type: "dinner",
      difficulty: "easy",
      image_url: null,
      prep_time_mins: 5,
      cook_time_mins: 15,
      servings: 2,
      tools: [],
      tags: ["#keto", "#quick-dinner", "#comfort-food"],
      ingredients: [{ id: 1, name: "cauliflower", amount: 1, unit: "head" }],
      steps: [{ id: 1, step_number: 1, instruction: "Pulse in food processor" }],
      created_at: "2026-11-20",
      updated_at: "2026-11-20",
    });

    render(
      <AuthContext.Provider value={mockAuth}>
        <MemoryRouter initialEntries={["/recipes/10"]}>
          <Routes>
            <Route path="/recipes/:id" element={<RecipeDetail />} />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>
    );

    expect(await screen.findByRole("heading", { name: "Keto Cauliflower Rice" })).toBeInTheDocument();
    expect(screen.getByText("Keto")).toBeInTheDocument();
    expect(screen.getByText("Quick Dinner")).toBeInTheDocument();
    expect(screen.getByText("Comfort Food")).toBeInTheDocument();
  });
});
