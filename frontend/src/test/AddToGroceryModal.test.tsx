import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { BrowserRouter } from "react-router-dom";
import { AddToGroceryModal } from "../components/AddToGroceryModal";
import { AuthContext, type AuthState } from "../context/auth";
import { api } from "../services/api";

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

const mockRecipes = [
  { id: 1, title: "Garlic Pasta", cook_time_mins: 20, difficulty: "easy", author_username: "chef1" },
  { id: 2, title: "Tomato Soup", cook_time_mins: 15, difficulty: "easy", author_username: "chef2" },
];

function renderWithAuth(ui: React.ReactElement, authState: Partial<AuthState> = {}) {
  const defaultAuth: AuthState = {
    user: { id: 1, username: "chef1", email: "chef1@test.com", role: "user" } as any,
    loading: false,
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
    setUser: vi.fn(),
    ...authState,
  };

  return render(
    <AuthContext.Provider value={defaultAuth}>
      <BrowserRouter>{ui}</BrowserRouter>
    </AuthContext.Provider>
  );
}

describe("US4.2.4: AddToGroceryModal", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(api, "searchRecipes").mockResolvedValue({
      items: mockRecipes as any,
      total: mockRecipes.length,
      limit: 50,
      offset: 0,
    });
  });

  it("Criterion 1: pre-selects the triggering recipe", async () => {
    renderWithAuth(<AddToGroceryModal isOpen={true} onClose={vi.fn()} initialRecipeId={1} />);

    await waitFor(() => {
      expect(screen.getByText("Garlic Pasta")).toBeInTheDocument();
    });

    const checkboxes = screen.getAllByRole("checkbox") as HTMLInputElement[];
    expect(checkboxes[0].checked).toBe(true);
    expect(checkboxes[1].checked).toBe(false);
    expect(screen.getByText(/1 selected/i)).toBeInTheDocument();
  });

  it("Criterion 2: allows multi-selecting and toggling recipes", async () => {
    renderWithAuth(<AddToGroceryModal isOpen={true} onClose={vi.fn()} initialRecipeId={1} />);

    await waitFor(() => {
      expect(screen.getByText("Tomato Soup")).toBeInTheDocument();
    });

    const checkboxes = screen.getAllByRole("checkbox") as HTMLInputElement[];
    fireEvent.click(checkboxes[1]); // select Tomato Soup

    expect(screen.getByText(/2 selected/i)).toBeInTheDocument();
    expect(checkboxes[0].checked).toBe(true);
    expect(checkboxes[1].checked).toBe(true);
  });

  it("Criterion 3 & 4: submits to API and navigates to /grocery on success", async () => {
    const mockGenerate = vi.spyOn(api, "generateGroceryList").mockResolvedValue({
      id: 10,
      user_id: 1,
      title: "Weekly Meal Prep",
      items: [],
      created_at: "2026-11-27",
      updated_at: "2026-11-27",
    });

    renderWithAuth(<AddToGroceryModal isOpen={true} onClose={vi.fn()} initialRecipeId={1} />);

    await waitFor(() => {
      expect(screen.getByText("Garlic Pasta")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /generate shopping list/i }));

    await waitFor(() => {
      expect(mockGenerate).toHaveBeenCalledWith({
        recipe_ids: [1],
        title: "Weekly Meal Prep",
      });
      expect(mockNavigate).toHaveBeenCalledWith("/grocery");
    });
  });

  it("Criterion 5: unauthenticated users are prompted to log in", async () => {
    renderWithAuth(
      <AddToGroceryModal isOpen={true} onClose={vi.fn()} initialRecipeId={1} />,
      { user: null }
    );

    await waitFor(() => {
      expect(screen.getByText("Garlic Pasta")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /generate shopping list/i }));

    await waitFor(() => {
      expect(
        screen.getByText(/Please log in or create an account to save grocery checklists/i)
      ).toBeInTheDocument();
    });
  });

  it("Criterion 6: submit button is disabled when zero recipes are selected", async () => {
    renderWithAuth(<AddToGroceryModal isOpen={true} onClose={vi.fn()} initialRecipeId={1} />);

    await waitFor(() => {
      expect(screen.getByText("Garlic Pasta")).toBeInTheDocument();
    });

    const checkboxes = screen.getAllByRole("checkbox") as HTMLInputElement[];
    fireEvent.click(checkboxes[0]); // uncheck Garlic Pasta

    expect(screen.getByText(/0 selected/i)).toBeInTheDocument();
    const submitBtn = screen.getByRole("button", { name: /generate shopping list/i });
    expect(submitBtn).toBeDisabled();
  });
});
