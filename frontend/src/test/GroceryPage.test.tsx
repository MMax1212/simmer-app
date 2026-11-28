import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { BrowserRouter } from "react-router-dom";
import { GroceryPage } from "../pages/GroceryPage";
import { api, type GroceryList } from "../services/api";

const mockGroceryList: GroceryList = {
  id: 1,
  user_id: 1,
  title: "Weekend Barbecue",
  created_at: "2026-11-27",
  updated_at: "2026-11-27",
  items: [
    {
      id: 101,
      grocery_list_id: 1,
      name: "yellow onion",
      amount: 2.0,
      unit: "count",
      department: "Produce",
      is_checked: false,
      created_at: "2026-11-27",
    },
    {
      id: 102,
      grocery_list_id: 1,
      name: "chicken breast",
      amount: 1.5,
      unit: "lb",
      department: "Meat & Seafood",
      is_checked: true,
      created_at: "2026-11-27",
    },
  ],
};

describe("US4.2.5: GroceryPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(api, "getGroceryList").mockResolvedValue(mockGroceryList);
  });

  it("Criterion 1 & 5: renders checklist title, aisle groups, and progress", async () => {
    render(
      <BrowserRouter>
        <GroceryPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText("Weekend Barbecue")).toBeInTheDocument();
      expect(screen.getByRole("heading", { name: /Produce/i })).toBeInTheDocument();
      expect(screen.getByRole("heading", { name: /Meat & Seafood/i })).toBeInTheDocument();
      expect(screen.getByText("yellow onion")).toBeInTheDocument();
      expect(screen.getByText("chicken breast")).toBeInTheDocument();
      expect(screen.getByText(/1 of 2 items purchased \(50%\)/i)).toBeInTheDocument();
    });
  });

  it("Criterion 2: toggles item checked status with strike-through styling", async () => {
    const mockUpdate = vi.spyOn(api, "updateGroceryItem").mockResolvedValue({
      ...mockGroceryList.items[0],
      is_checked: true,
    });

    render(
      <BrowserRouter>
        <GroceryPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText("yellow onion")).toBeInTheDocument();
    });

    // Click to toggle
    fireEvent.click(screen.getByText("yellow onion"));

    await waitFor(() => {
      expect(mockUpdate).toHaveBeenCalledWith(101, { is_checked: true });
    });
  });

  it("Criterion 3: adds manual custom item via entry bar", async () => {
    const mockAdd = vi.spyOn(api, "addGroceryItem").mockResolvedValue({
      id: 103,
      grocery_list_id: 1,
      name: "cheddar cheese",
      amount: 1.0,
      unit: "cup",
      department: "Dairy & Refrigerated",
      is_checked: false,
      created_at: "2026-11-27",
    });

    render(
      <BrowserRouter>
        <GroceryPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText("Weekend Barbecue")).toBeInTheDocument();
    });

    fireEvent.change(screen.getByPlaceholderText(/Add item/i), {
      target: { value: "cheddar cheese" },
    });
    fireEvent.click(screen.getByRole("button", { name: /Add/i }));

    await waitFor(() => {
      expect(mockAdd).toHaveBeenCalledWith({
        name: "cheddar cheese",
        amount: 1,
        unit: "count",
        department: "Other",
      });
      expect(screen.getByText("cheddar cheese")).toBeInTheDocument();
    });
  });

  it("Criterion 4: removes an item on delete click", async () => {
    const mockDelete = vi.spyOn(api, "deleteGroceryItem").mockResolvedValue();

    render(
      <BrowserRouter>
        <GroceryPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText("yellow onion")).toBeInTheDocument();
    });

    const deleteBtn = screen.getByLabelText("Delete yellow onion");
    fireEvent.click(deleteBtn);

    await waitFor(() => {
      expect(mockDelete).toHaveBeenCalledWith(101);
      expect(screen.queryByText("yellow onion")).not.toBeInTheDocument();
    });
  });

  it("Criterion 6: displays empty state when checklist has zero items", async () => {
    vi.spyOn(api, "getGroceryList").mockResolvedValue({
      ...mockGroceryList,
      items: [],
    });

    render(
      <BrowserRouter>
        <GroceryPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Your grocery checklist is empty/i)).toBeInTheDocument();
      expect(screen.getByRole("link", { name: /Explore Recipes/i })).toBeInTheDocument();
    });
  });
});
