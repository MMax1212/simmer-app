import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { UserSearchInput } from "../components/UserSearchInput";
import type { UserSearchResultItem, UserSearchResponse } from "../services/api";

const respond = (data: unknown, status = 200) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });

const fetchMock = vi.fn<typeof fetch>();

beforeEach(() => {
  vi.stubGlobal("fetch", fetchMock);
  fetchMock.mockReset();
  localStorage.clear();
});

const mockUsers: UserSearchResultItem[] = [
  {
    id: 101,
    username: "mario_chef",
    bio: "Passionate pasta maker",
    avatar_url: "https://example.com/mario.jpg",
    culinary_preferences: ["Italian"],
    created_at: "2026-01-01T00:00:00Z",
    is_following: false,
    followers_count: 12,
    following_count: 5,
  },
  {
    id: 102,
    username: "luigi_bakes",
    bio: "Artisan sourdough and pastries",
    avatar_url: null,
    culinary_preferences: ["Baking"],
    created_at: "2026-01-02T00:00:00Z",
    is_following: true,
    followers_count: 34,
    following_count: 20,
  },
];

const mockSearchResponse: UserSearchResponse = {
  total: 2,
  limit: 10,
  offset: 0,
  items: mockUsers,
};

function renderComponent(props = {}) {
  return render(
    <BrowserRouter>
      <UserSearchInput {...props} />
    </BrowserRouter>
  );
}

describe("US4.1.3: UserSearchInput Component", () => {
  it("renders search input with default placeholder and accessibility attributes (AC1, AC2)", () => {
    renderComponent();

    const input = screen.getByRole("combobox");
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute("placeholder", "Search chefs & friends...");
    expect(input).toHaveAttribute("aria-expanded", "false");
    expect(input).toHaveAttribute("aria-autocomplete", "list");
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
  });

  it("waits 300ms debounce before dispatching search request (AC1)", async () => {
    fetchMock.mockResolvedValue(respond(mockSearchResponse));
    const user = userEvent.setup();
    renderComponent();

    const input = screen.getByRole("combobox");
    await user.type(input, "mar");

    // Immediately after typing, fetch should not have fired yet due to 300ms debounce
    expect(fetchMock).not.toHaveBeenCalled();

    // After debounce expires, API is called
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(1);
    });

    const calledUrl = String(fetchMock.mock.calls[0][0]);
    expect(calledUrl).toContain("/api/v1/users/search");
    expect(calledUrl).toContain("q=mar");
  });

  it("renders live dropdown results with username, bio, follower count and avatar (AC4)", async () => {
    fetchMock.mockResolvedValue(respond(mockSearchResponse));
    const user = userEvent.setup();
    renderComponent();

    const input = screen.getByRole("combobox");
    await user.type(input, "chef");

    // Wait for debounce and fetch to populate user results
    expect(await screen.findByText("@mario_chef")).toBeInTheDocument();
    expect(screen.getByRole("listbox")).toBeInTheDocument();
    expect(screen.getByText(/12 followers/i)).toBeInTheDocument();
    expect(screen.getByText(/Passionate pasta maker/i)).toBeInTheDocument();

    expect(screen.getByText("@luigi_bakes")).toBeInTheDocument();
    expect(screen.getByText(/34 followers/i)).toBeInTheDocument();

    // FollowButtons rendered for each user
    const followButtons = screen.getAllByRole("button", { name: /follow/i });
    expect(followButtons.length).toBeGreaterThanOrEqual(2);
  });

  it("closes dropdown and does not search when query is empty or whitespace only (AC2)", async () => {
    fetchMock.mockResolvedValue(respond(mockSearchResponse));
    const user = userEvent.setup();
    renderComponent();

    const input = screen.getByRole("combobox");
    await user.type(input, "   ");

    // Give time to ensure no search is dispatched
    await new Promise((r) => setTimeout(r, 350));
    expect(fetchMock).not.toHaveBeenCalled();
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
  });

  it("supports keyboard navigation with ArrowDown and ArrowUp (AC5, AC6)", async () => {
    fetchMock.mockResolvedValue(respond(mockSearchResponse));
    const user = userEvent.setup();
    renderComponent();

    const input = screen.getByRole("combobox");
    await user.type(input, "mario");

    expect(await screen.findByText("@mario_chef")).toBeInTheDocument();
    const options = screen.getAllByRole("option");
    expect(options).toHaveLength(2);

    // Initial state: none selected
    expect(options[0]).toHaveAttribute("aria-selected", "false");
    expect(options[1]).toHaveAttribute("aria-selected", "false");

    // ArrowDown highlights first option
    fireEvent.keyDown(input, { key: "ArrowDown" });
    expect(options[0]).toHaveAttribute("aria-selected", "true");
    expect(options[1]).toHaveAttribute("aria-selected", "false");

    // ArrowDown again highlights second option
    fireEvent.keyDown(input, { key: "ArrowDown" });
    expect(options[0]).toHaveAttribute("aria-selected", "false");
    expect(options[1]).toHaveAttribute("aria-selected", "true");

    // ArrowUp returns highlight to first option
    fireEvent.keyDown(input, { key: "ArrowUp" });
    expect(options[0]).toHaveAttribute("aria-selected", "true");
    expect(options[1]).toHaveAttribute("aria-selected", "false");
  });

  it("selects highlighted user when Enter is pressed (AC7)", async () => {
    fetchMock.mockResolvedValue(respond(mockSearchResponse));
    const onSelectUser = vi.fn();
    const user = userEvent.setup();
    renderComponent({ onSelectUser });

    const input = screen.getByRole("combobox");
    await user.type(input, "mario");

    expect(await screen.findByText("@mario_chef")).toBeInTheDocument();

    // Navigate to second item and press Enter
    fireEvent.keyDown(input, { key: "ArrowDown" });
    fireEvent.keyDown(input, { key: "ArrowDown" });
    fireEvent.keyDown(input, { key: "Enter" });

    expect(onSelectUser).toHaveBeenCalledWith(mockUsers[1]);
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
  });

  it("selects user when clicking on result item (AC7)", async () => {
    fetchMock.mockResolvedValue(respond(mockSearchResponse));
    const onSelectUser = vi.fn();
    const user = userEvent.setup();
    renderComponent({ onSelectUser });

    const input = screen.getByRole("combobox");
    await user.type(input, "mario");

    const userOption = await screen.findByText("@mario_chef");
    await user.click(userOption);

    expect(onSelectUser).toHaveBeenCalledWith(mockUsers[0]);
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
  });

  it("closes dropdown when Escape key is pressed (AC8)", async () => {
    fetchMock.mockResolvedValue(respond(mockSearchResponse));
    const user = userEvent.setup();
    renderComponent();

    const input = screen.getByRole("combobox");
    await user.type(input, "mario");

    expect(await screen.findByRole("listbox")).toBeInTheDocument();

    fireEvent.keyDown(input, { key: "Escape" });
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
  });

  it("dismisses dropdown when clicking outside (AC8)", async () => {
    fetchMock.mockResolvedValue(respond(mockSearchResponse));
    const user = userEvent.setup();
    render(
      <div>
        <div data-testid="outside-area">Outside</div>
        <BrowserRouter>
          <UserSearchInput />
        </BrowserRouter>
      </div>
    );

    const input = screen.getByRole("combobox");
    await user.type(input, "mario");

    expect(await screen.findByRole("listbox")).toBeInTheDocument();

    // Click outside
    fireEvent.mouseDown(screen.getByTestId("outside-area"));
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
  });

  it("displays empty state feedback when no users match query (AC3)", async () => {
    fetchMock.mockResolvedValue(
      respond({ total: 0, limit: 10, offset: 0, items: [] })
    );
    const user = userEvent.setup();
    renderComponent();

    const input = screen.getByRole("combobox");
    await user.type(input, "nonexistent");

    expect(await screen.findByText(/No cooks found matching/i)).toBeInTheDocument();
  });

  it("displays error message when search API request fails", async () => {
    fetchMock.mockResolvedValue(respond({ detail: "Database connection failed" }, 500));
    const user = userEvent.setup();
    renderComponent();

    const input = screen.getByRole("combobox");
    await user.type(input, "chef");

    expect(await screen.findByText(/Database connection failed/i)).toBeInTheDocument();
  });

  it("clears search input and results when clear (X) button is clicked", async () => {
    fetchMock.mockResolvedValue(respond(mockSearchResponse));
    const user = userEvent.setup();
    renderComponent();

    const input = screen.getByRole("combobox");
    await user.type(input, "chef");

    expect(await screen.findByRole("listbox")).toBeInTheDocument();

    const clearButton = screen.getByRole("button", { name: "Clear search" });
    await user.click(clearButton);

    expect(input).toHaveValue("");
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
  });

  it("updates follow state on inline FollowButton toggle without selecting row (AC9)", async () => {
    fetchMock.mockImplementation(async (url) => {
      const urlStr = String(url);
      if (urlStr.includes("/users/search")) {
        return respond(mockSearchResponse);
      }
      if (urlStr.includes("/follow")) {
        return respond({ following: true, followers_count: 13, following_count: 5 });
      }
      return respond([]);
    });

    const onSelectUser = vi.fn();
    const user = userEvent.setup();
    renderComponent({ onSelectUser });

    const input = screen.getByRole("combobox");
    await user.type(input, "chef");

    // Wait for search results to load
    expect(await screen.findByText("@mario_chef")).toBeInTheDocument();

    // Click the follow button for mario_chef (targetUserId: 101, currently initialFollowing: false)
    const followButtons = screen.getAllByRole("button", { name: /^follow mario_chef$/i });
    expect(followButtons[0]).toBeInTheDocument();

    await user.click(followButtons[0]);

    // Row selection should NOT have triggered
    expect(onSelectUser).not.toHaveBeenCalled();

    // FollowButton updates to "Following"
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /^following mario_chef$/i })).toBeInTheDocument();
    });
  });
});
