import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { Home } from "../pages/Home";
import { BrowserRouter } from "react-router-dom";
import * as AuthContext from "../context/auth";
import type { FeedResponse, User } from "../services/api";

const respond = (data: unknown, status = 200) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });

const fetchMock = vi.fn<typeof fetch>();

const mockUser: User = {
  id: 1,
  username: "bryan",
  email: "bryan@example.com",
  role: "user",
  is_active: true,
  bio: "Chef Bryan",
  avatar_url: null,
  culinary_preferences: ["Mexican", "Italian"],
  created_at: "2026-11-01",
};

const mockFeedItem = {
  id: 10,
  caption: "Fresh homemade sourdough straight from the Dutch oven!",
  image_url: "https://images.unsplash.com/photo-sourdough.jpg",
  media_type: "image",
  created_at: "2026-11-13T12:00:00",
  author: {
    id: 2,
    username: "mario_bakes",
    avatar_url: "https://images.unsplash.com/avatar-mario.jpg",
  },
  recipe: {
    id: 5,
    title: "Artisan Sourdough Loaf",
    cook_time_mins: 45,
    difficulty: "hard",
  },
};

const mockFeedResponse: FeedResponse = {
  total: 1,
  limit: 20,
  offset: 0,
  items: [mockFeedItem],
};

const mockEmptyFeedResponse: FeedResponse = {
  total: 0,
  limit: 20,
  offset: 0,
  items: [],
};

beforeEach(() => {
  vi.stubGlobal("fetch", fetchMock);
  fetchMock.mockReset();
  localStorage.clear();
});

// Each endpoint gets a fresh response body; parallel discovery must not consume the feed's.
function mockHomeRequests(feed: FeedResponse) {
  fetchMock.mockImplementation(async (url) => {
    if (String(url).includes("/recipes/trending")) return respond([]);
    if (String(url).includes("/recipes")) {
      return respond({ items: [], total: 0, limit: 20, offset: 0 });
    }
    return respond(feed);
  });
}

function renderHome(currentUser: User | null = mockUser) {
  vi.spyOn(AuthContext, "useAuth").mockReturnValue({
    user: currentUser,
    loading: false,
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
    setUser: vi.fn(),
  });

  return render(
    <BrowserRouter>
      <Home />
    </BrowserRouter>
  );
}

// Keep the existing feed regressions alongside discovery: adding a parallel Home
// request must not change the default tab, login prompt, empty state, or follow actions.
describe("US3.5.5: Tabbed Home Feed UI (Following Feed vs Global Community Feed)", () => {
  it("renders tabs for 'Following Feed' and 'Global Community Feed' (AC1)", async () => {
    mockHomeRequests(mockFeedResponse);
    renderHome(mockUser);

    expect(screen.getByRole("tab", { name: /following/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /global/i })).toBeInTheDocument();
  });

  it("loads Following Feed by default for logged-in user and displays feed card (AC2)", async () => {
    mockHomeRequests(mockFeedResponse);
    renderHome(mockUser);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/feed?mode=following"),
        expect.anything()
      );
    });

    expect(await screen.findByText("Fresh homemade sourdough straight from the Dutch oven!")).toBeInTheDocument();
    expect(screen.getByText("mario_bakes")).toBeInTheDocument();
    expect(screen.getByText("Artisan Sourdough Loaf")).toBeInTheDocument();
  });

  it("displays empty state when Following Feed has no posts with prompt to explore global (AC3)", async () => {
    mockHomeRequests(mockEmptyFeedResponse);
    renderHome(mockUser);

    expect(await screen.findByText(/your following feed is empty/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /explore global community/i })).toBeInTheDocument();
  });

  it("switches to Global Community Feed when clicking the Global tab (AC4)", async () => {
    const actor = userEvent.setup();
    mockHomeRequests(mockFeedResponse);
    renderHome(mockUser);

    const globalTab = screen.getByRole("tab", { name: /global/i });
    await actor.click(globalTab);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/feed?mode=global"),
        expect.anything()
      );
    });
  });

  it("prompts unauthenticated visitors to log in when viewing Following Feed (AC5)", async () => {
    const actor = userEvent.setup();
    mockHomeRequests(mockFeedResponse);
    renderHome(null); // Anonymous visitor

    // Default for unauthenticated is Global Community Feed
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/feed?mode=global"),
        expect.anything()
      );
    });

    // When clicking Following tab
    const followingTab = screen.getByRole("tab", { name: /following/i });
    await actor.click(followingTab);

    expect(screen.getByText(/sign in to see posts from creators you follow/i)).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: /log in/i }).length).toBeGreaterThanOrEqual(1);
  });

  it("renders interactive FollowButton on feed cards for post author (AC6)", async () => {
    mockHomeRequests(mockFeedResponse);
    renderHome(mockUser);

    const followButton = await screen.findByRole("button", { name: /follow mario_bakes/i });
    expect(followButton).toBeInTheDocument();
  });
});
