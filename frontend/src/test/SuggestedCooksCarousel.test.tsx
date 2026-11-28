import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AuthProvider } from "../context/AuthProvider";
import { SuggestedCooksCarousel } from "../components/SuggestedCooksCarousel";
import type { UserSearchResultItem } from "../services/api";

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

const mockCooks: UserSearchResultItem[] = [
  {
    id: 201,
    username: "gordon_chef",
    bio: "Passionate pastry chef and mentor",
    avatar_url: "https://example.com/gordon.jpg",
    culinary_preferences: ["French", "Baking"],
    created_at: "2026-01-01T00:00:00Z",
    is_following: false,
    followers_count: 52,
    following_count: 10,
  },
  {
    id: 202,
    username: "julia_bakes",
    bio: "Rustic breads and pies",
    avatar_url: null,
    culinary_preferences: ["Bread"],
    created_at: "2026-01-02T00:00:00Z",
    is_following: false,
    followers_count: 38,
    following_count: 14,
  },
];

function renderCarousel() {
  return render(
    <AuthProvider>
      <BrowserRouter>
        <SuggestedCooksCarousel />
      </BrowserRouter>
    </AuthProvider>
  );
}

describe("US4.1.5: SuggestedCooksCarousel Component", () => {
  it("renders loading indicator while suggested cooks are being fetched (AC1)", () => {
    fetchMock.mockImplementation(() => new Promise(() => {})); // Never resolves
    renderCarousel();

    expect(screen.getByText("Finding culinary creators for you...")).toBeInTheDocument();
  });

  it("renders suggested cook cards with username, followers, bio, and follow button (AC1, AC5)", async () => {
    fetchMock.mockImplementation(async () => respond(mockCooks));
    renderCarousel();

    // Wait for suggested cooks to load
    expect(await screen.findByText("@gordon_chef")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Suggested Cooks to Follow" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Explore all" })).toHaveAttribute("href", "/friends");

    // Cards
    expect(screen.getByTestId("suggested-followers-201")).toHaveTextContent("52 followers");
    expect(screen.getByText("Passionate pastry chef and mentor")).toBeInTheDocument();
    expect(screen.getByText("French")).toBeInTheDocument();

    expect(screen.getByText("@julia_bakes")).toBeInTheDocument();
    expect(screen.getByTestId("suggested-followers-202")).toHaveTextContent("38 followers");

    // Follow buttons
    const followButtons = screen.getAllByRole("button", { name: /follow/i });
    expect(followButtons.length).toBeGreaterThanOrEqual(2);
  });

  it("renders error state and retries fetching when clicking retry button", async () => {
    fetchMock.mockImplementationOnce(async () => respond({ detail: "Database unavailable" }, 500));
    fetchMock.mockImplementation(async () => respond(mockCooks));
    renderCarousel();

    expect(await screen.findByText(/Could not load suggested cooks: Database unavailable/i)).toBeInTheDocument();

    const user = userEvent.setup();
    const retryButton = screen.getByRole("button", { name: "Retry" });
    await user.click(retryButton);

    expect(await screen.findByText("@gordon_chef")).toBeInTheDocument();
  });

  it("renders nothing when no suggestions exist (AC1)", async () => {
    fetchMock.mockImplementation(async () => respond([]));
    const { container } = renderCarousel();

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalled();
    });

    expect(container).toBeEmptyDOMElement();
  });

  it("scrolls list left and right when clicking previous and next buttons (AC5)", async () => {
    fetchMock.mockImplementation(async () => respond(mockCooks));
    const user = userEvent.setup();
    renderCarousel();

    expect(await screen.findByText("@gordon_chef")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Suggested Cooks to Follow" })).toBeInTheDocument();

    const list = screen.getByRole("region", { name: "Suggested cooks list" });
    const scrollByMock = vi.fn();
    list.scrollBy = scrollByMock;

    const prevButton = screen.getByRole("button", { name: "Previous suggested cooks" });
    const nextButton = screen.getByRole("button", { name: "Next suggested cooks" });

    await user.click(nextButton);
    expect(scrollByMock).toHaveBeenCalledWith(expect.objectContaining({ left: 280 }));

    await user.click(prevButton);
    expect(scrollByMock).toHaveBeenCalledWith(expect.objectContaining({ left: -280 }));
  });

  it("optimistically toggles follow state and updates follower count on card (AC6)", async () => {
    fetchMock.mockImplementation(async (url) => {
      const urlStr = String(url);
      if (urlStr.includes("/api/v1/users/suggested")) {
        return respond(mockCooks);
      }
      if (urlStr.includes("/users/201/follow")) {
        return respond({ following: true, followers_count: 53, following_count: 10 });
      }
      return respond([]);
    });

    const user = userEvent.setup();
    renderCarousel();

    expect(await screen.findByText("@gordon_chef")).toBeInTheDocument();
    expect(screen.getByTestId("suggested-followers-201")).toHaveTextContent("52 followers");

    const followButton = screen.getByRole("button", { name: /^follow gordon_chef$/i });
    await user.click(followButton);

    // Button should optimistically update to Following and follower count should be 53
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /^following gordon_chef$/i })).toBeInTheDocument();
      expect(screen.getByTestId("suggested-followers-201")).toHaveTextContent("53 followers");
    });
  });
});
