import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "../App";
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

  fetchMock.mockImplementation(async (url) => {
    const urlStr = String(url);
    if (urlStr.includes("/api/v1/users/search")) {
      return respond(mockDirectoryResponse);
    }
    if (urlStr.includes("/api/v1/feed")) {
      return respond({ total: 0, limit: 20, offset: 0, items: [] });
    }
    if (urlStr.includes("/api/v1/recipes")) {
      return respond({ total: 0, limit: 20, offset: 0, items: [] });
    }
    return respond([]);
  });
});

const mockChefs: UserSearchResultItem[] = [
  {
    id: 101,
    username: "mario_chef",
    bio: "Passionate pasta and sourdough creator",
    avatar_url: "https://example.com/mario.jpg",
    culinary_preferences: ["Italian", "Pasta", "Bread"],
    created_at: "2026-01-01T00:00:00Z",
    is_following: false,
    followers_count: 24,
    following_count: 8,
  },
  {
    id: 102,
    username: "luigi_bakes",
    bio: "Artisan baker and pastry lover",
    avatar_url: null,
    culinary_preferences: ["French", "Pastries"],
    created_at: "2026-01-02T00:00:00Z",
    is_following: true,
    followers_count: 45,
    following_count: 15,
  },
];

const mockDirectoryResponse: UserSearchResponse = {
  total: 2,
  limit: 50,
  offset: 0,
  items: mockChefs,
};

function open(path: string, signedIn = false) {
  window.history.replaceState(null, "", path);
  if (signedIn) localStorage.setItem("simmer_token", "valid-token");
  return render(<App />);
}

describe("US4.1.4: Find Chefs & Friends Directory Page", () => {
  it("renders page heading and initial active chef cards at /friends (AC1, AC3)", async () => {
    open("/friends");

    // Header and search bar exist
    expect(await screen.findByRole("heading", { name: /find chefs & friends/i })).toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: /search chefs by username/i })).toBeInTheDocument();

    // Renders chef cards
    expect(await screen.findByText("@mario_chef")).toBeInTheDocument();
    expect(screen.getByText("Passionate pasta and sourdough creator")).toBeInTheDocument();
    expect(screen.getByText("Italian")).toBeInTheDocument();
    expect(screen.getByTestId("followers-count-101")).toHaveTextContent("24 followers");

    expect(screen.getByText("@luigi_bakes")).toBeInTheDocument();
    expect(screen.getByTestId("followers-count-102")).toHaveTextContent("45 followers");
  });

  it("initializes search query from URL query parameter ?q=mario (AC2)", async () => {
    fetchMock.mockImplementation(async (url) => {
      const urlStr = String(url);
      if (urlStr.includes("q=mario")) {
        return respond({
          total: 1,
          limit: 50,
          offset: 0,
          items: [mockChefs[0]],
        });
      }
      return respond(mockDirectoryResponse);
    });

    open("/friends?q=mario");

    const input = screen.getByRole("textbox", { name: /search chefs by username/i });
    expect(input).toHaveValue("mario");

    // Should fetch with q=mario
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalled();
      const calledUrl = String(fetchMock.mock.calls[0][0]);
      expect(calledUrl).toContain("q=mario");
    });

    expect(await screen.findByText("@mario_chef")).toBeInTheDocument();
    expect(screen.queryByText("@luigi_bakes")).not.toBeInTheDocument();
  });

  it("filters directory when typing into the search input with debounce (AC1, AC2)", async () => {
    fetchMock.mockImplementation(async (url) => {
      const urlStr = String(url);
      if (urlStr.includes("q=luigi")) {
        return respond({
          total: 1,
          limit: 50,
          offset: 0,
          items: [mockChefs[1]],
        });
      }
      return respond(mockDirectoryResponse);
    });

    const user = userEvent.setup();
    open("/friends");

    expect(await screen.findByText("@mario_chef")).toBeInTheDocument();

    const input = screen.getByRole("textbox", { name: /search chefs by username/i });
    await user.type(input, "luigi");

    // Wait for debounced search to fire and populate matching chef
    expect(await screen.findByText("@luigi_bakes")).toBeInTheDocument();
    expect(screen.queryByText("@mario_chef")).not.toBeInTheDocument();
  });

  it("displays empty state with 'Clear search' button when no chefs match query (AC6)", async () => {
    fetchMock.mockImplementation(async (url) => {
      const urlStr = String(url);
      if (urlStr.includes("q=nobody")) {
        return respond({ total: 0, limit: 50, offset: 0, items: [] });
      }
      return respond(mockDirectoryResponse);
    });

    const user = userEvent.setup();
    open("/friends");

    expect(await screen.findByText("@mario_chef")).toBeInTheDocument();

    const input = screen.getByRole("textbox", { name: /search chefs by username/i });
    await user.type(input, "nobody");

    // Empty state appears
    expect(await screen.findByRole("heading", { name: "No chefs found" })).toBeInTheDocument();
    expect(screen.getByText(/We couldn't find any cooks matching "nobody"/i)).toBeInTheDocument();

    // Clicking 'Clear search' resets the search and reloads directory
    const clearButton = screen.getByRole("button", { name: "Clear search" });
    await user.click(clearButton);

    expect(input).toHaveValue("");
    expect(await screen.findByText("@mario_chef")).toBeInTheDocument();
    expect(screen.getByText("@luigi_bakes")).toBeInTheDocument();
  });

  it("optimistically updates follow button and follower count on card toggle (AC4, AC5)", async () => {
    fetchMock.mockImplementation(async (url) => {
      const urlStr = String(url);
      if (urlStr.includes("/users/search")) {
        return respond(mockDirectoryResponse);
      }
      if (urlStr.includes("/users/101/follow")) {
        return respond({ following: true, followers_count: 25, following_count: 8 });
      }
      return respond([]);
    });

    const user = userEvent.setup();
    open("/friends");

    expect(await screen.findByText("@mario_chef")).toBeInTheDocument();
    expect(screen.getByTestId("followers-count-101")).toHaveTextContent("24 followers");

    // Follow button for mario_chef
    const followButton = screen.getByRole("button", { name: /^follow mario_chef$/i });
    await user.click(followButton);

    // Follower count updates to 25 and button switches to Following
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /^following mario_chef$/i })).toBeInTheDocument();
      expect(screen.getByTestId("followers-count-101")).toHaveTextContent("25 followers");
    });
  });

  it("renders 'Find Friends' link in Navbar and navigates to /friends", async () => {
    const user = userEvent.setup();
    open("/");

    const findFriendsLink = screen.getByRole("link", { name: /find friends/i });
    expect(findFriendsLink).toBeInTheDocument();
    expect(findFriendsLink).toHaveAttribute("href", "/friends");

    await user.click(findFriendsLink);
    expect(await screen.findByRole("heading", { name: /find chefs & friends/i })).toBeInTheDocument();
  });
});
