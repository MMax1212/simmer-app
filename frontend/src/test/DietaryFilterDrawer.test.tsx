import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "../App";
import { DietaryFilterDrawer } from "../components/DietaryFilterDrawer";
import { api, type RecipeSearchResult } from "../services/api";

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

const mockSearchResult: RecipeSearchResult = {
  total: 1,
  limit: 20,
  offset: 0,
  items: [
    {
      id: 1,
      title: "Vegan Lentil Soup",
      author_username: "chef_ana",
      cuisine: "Mediterranean",
      meal_type: "dinner",
      difficulty: "easy",
      cook_time_mins: 20,
      image_url: null,
    },
  ],
};

describe("US4.4.3: Dietary & Occasion Filter Drawer Component", () => {
  // --- AC1: API Parameter Serialization ---
  it("US4.4.3: api.searchRecipes serializes dietary, occasion, and max_time query params (AC1)", async () => {
    fetchMock.mockResolvedValue(respond(mockSearchResult));

    await api.searchRecipes({
      dietary: "vegan,gluten-free",
      occasion: "quick-dinner",
      max_time: 30,
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const calledUrl = fetchMock.mock.calls[0][0] as string;
    expect(calledUrl).toContain("dietary=vegan%2Cgluten-free");
    expect(calledUrl).toContain("occasion=quick-dinner");
    expect(calledUrl).toContain("max_time=30");
  });

  // --- AC2: Drawer Visibility & Accessibility ---
  it("US4.4.3: renders drawer dialog when isOpen is true (AC2)", () => {
    const handleClose = vi.fn();
    render(
      <DietaryFilterDrawer
        isOpen={true}
        onClose={handleClose}
        selectedDietary={[]}
        onDietaryChange={vi.fn()}
        selectedOccasion={null}
        onOccasionChange={vi.fn()}
        selectedMaxTime={null}
        onMaxTimeChange={vi.fn()}
        onClearAll={vi.fn()}
      />
    );

    const dialog = screen.getByRole("dialog", { name: /filter recipes/i });
    expect(dialog).toBeInTheDocument();
    expect(screen.getByText(/dietary preferences/i)).toBeInTheDocument();
    expect(screen.getByText(/occasions/i)).toBeInTheDocument();
    expect(screen.getByText(/max cooking time/i)).toBeInTheDocument();
  });

  it("US4.4.3: does not render drawer when isOpen is false (AC2)", () => {
    render(
      <DietaryFilterDrawer
        isOpen={false}
        onClose={vi.fn()}
        selectedDietary={[]}
        onDietaryChange={vi.fn()}
        selectedOccasion={null}
        onOccasionChange={vi.fn()}
        selectedMaxTime={null}
        onMaxTimeChange={vi.fn()}
        onClearAll={vi.fn()}
      />
    );

    expect(screen.queryByRole("dialog", { name: /filter recipes/i })).not.toBeInTheDocument();
  });

  // --- AC3: Multi-select Dietary Chips ---
  it("US4.4.3: multi-select dietary chips toggle active state and support multiple selections (AC3)", async () => {
    const actor = userEvent.setup();
    const handleDietaryChange = vi.fn();

    render(
      <DietaryFilterDrawer
        isOpen={true}
        onClose={vi.fn()}
        selectedDietary={["#vegan"]}
        onDietaryChange={handleDietaryChange}
        selectedOccasion={null}
        onOccasionChange={vi.fn()}
        selectedMaxTime={null}
        onMaxTimeChange={vi.fn()}
        onClearAll={vi.fn()}
      />
    );

    // #vegan is selected, clicking it should toggle off
    const veganChip = screen.getByRole("button", { name: "Vegan" });
    expect(veganChip).toHaveClass("on");
    await actor.click(veganChip);
    expect(handleDietaryChange).toHaveBeenCalledWith([]);

    // Clicking Gluten-Free adds it
    const gfChip = screen.getByRole("button", { name: "Gluten-Free" });
    expect(gfChip).not.toHaveClass("on");
    await actor.click(gfChip);
    expect(handleDietaryChange).toHaveBeenCalledWith(["#vegan", "#gluten-free"]);
  });

  // --- AC4: Occasion Chip Selection ---
  it("US4.4.3: occasion badge chip toggles selection (AC4)", async () => {
    const actor = userEvent.setup();
    const handleOccasionChange = vi.fn();

    render(
      <DietaryFilterDrawer
        isOpen={true}
        onClose={vi.fn()}
        selectedDietary={[]}
        onDietaryChange={vi.fn()}
        selectedOccasion={null}
        onOccasionChange={handleOccasionChange}
        selectedMaxTime={null}
        onMaxTimeChange={vi.fn()}
        onClearAll={vi.fn()}
      />
    );

    const quickDinnerChip = screen.getByRole("button", { name: "Quick Dinner" });
    await actor.click(quickDinnerChip);
    expect(handleOccasionChange).toHaveBeenCalledWith("#quick-dinner");
  });

  // --- AC5: Max Cooking Time Selection ---
  it("US4.4.3: maximum cooking time selector sets duration constraint (AC5)", async () => {
    const actor = userEvent.setup();
    const handleMaxTimeChange = vi.fn();

    render(
      <DietaryFilterDrawer
        isOpen={true}
        onClose={vi.fn()}
        selectedDietary={[]}
        onDietaryChange={vi.fn()}
        selectedOccasion={null}
        onOccasionChange={vi.fn()}
        selectedMaxTime={null}
        onMaxTimeChange={handleMaxTimeChange}
        onClearAll={vi.fn()}
      />
    );

    const time30Chip = screen.getByRole("button", { name: "≤ 30 mins" });
    await actor.click(time30Chip);
    expect(handleMaxTimeChange).toHaveBeenCalledWith(30);
  });

  // --- AC6: Clear All Filters ---
  it("US4.4.3: Clear All Filters resets selections (AC6)", async () => {
    const actor = userEvent.setup();
    const handleClearAll = vi.fn();

    render(
      <DietaryFilterDrawer
        isOpen={true}
        onClose={vi.fn()}
        selectedDietary={["#vegan"]}
        onDietaryChange={vi.fn()}
        selectedOccasion={"#quick-dinner"}
        onOccasionChange={vi.fn()}
        selectedMaxTime={30}
        onMaxTimeChange={vi.fn()}
        onClearAll={handleClearAll}
      />
    );

    const clearBtn = screen.getByRole("button", { name: /clear all/i });
    await actor.click(clearBtn);
    expect(handleClearAll).toHaveBeenCalledTimes(1);
  });

  // --- AC7: Integration with RecipesPage ---
  it("US4.4.3: RecipesPage toggles drawer and dispatches filtered search (AC7)", async () => {
    const actor = userEvent.setup();
    fetchMock.mockResolvedValue(respond(mockSearchResult));

    window.history.replaceState(null, "", "/recipes");
    render(<App />);

    // Open button should exist on /recipes
    const filterBtn = await screen.findByRole("button", { name: /filters/i });
    expect(filterBtn).toBeInTheDocument();

    // Clicking opens the drawer
    await actor.click(filterBtn);
    expect(screen.getByRole("dialog", { name: /filter recipes/i })).toBeInTheDocument();

    // Select Vegan chip inside drawer
    const veganChip = screen.getByRole("button", { name: "Vegan" });
    await actor.click(veganChip);

    // Close / Apply drawer
    const applyBtn = screen.getByRole("button", { name: /apply filters/i });
    await actor.click(applyBtn);

    // Verify search was dispatched with dietary=vegan
    await waitFor(() => {
      const calls = fetchMock.mock.calls.map((c) => c[0] as string);
      expect(calls.some((url) => url.includes("dietary=vegan"))).toBe(true);
    });
  });
});
