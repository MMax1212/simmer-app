import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { FollowButton } from "../components/FollowButton";
import { type FollowToggleResponse } from "../services/api";

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

describe("US3.5.4: Interactive FollowButton Component", () => {
  // --- AC1: Initial visual state when not following ---
  it("renders 'Follow' button with correct aria attributes when not following (AC1)", () => {
    render(<FollowButton targetUserId={42} initialFollowing={false} />);

    const button = screen.getByRole("button", { name: /follow/i });
    expect(button).toBeInTheDocument();
    expect(button).toHaveTextContent("Follow");
    expect(button).toHaveAttribute("aria-pressed", "false");
  });

  // --- AC2: Initial visual state when already following ---
  it("renders 'Following' button when already following (AC2)", () => {
    render(<FollowButton targetUserId={42} initialFollowing={true} />);

    const button = screen.getByRole("button", { name: /following/i });
    expect(button).toBeInTheDocument();
    expect(button).toHaveTextContent("Following");
    expect(button).toHaveAttribute("aria-pressed", "true");
  });

  // --- AC3: Follower count display ---
  it("displays follower count when showCount is true (AC3)", () => {
    render(
      <FollowButton
        targetUserId={42}
        initialFollowing={false}
        initialFollowersCount={15}
        showCount={true}
      />
    );

    expect(screen.getByText("15")).toBeInTheDocument();
  });

  // --- AC4: Self-follow guard ---
  it("does not render when targetUserId matches currentUserId (AC4)", () => {
    const { container } = render(
      <FollowButton targetUserId={99} currentUserId={99} initialFollowing={false} />
    );

    expect(container.firstChild).toBeNull();
  });

  // --- AC5: Optimistic toggle from unfollowed to followed ---
  it("optimistically updates to 'Following' and increments count on click (AC5)", async () => {
    const actor = userEvent.setup();
    let resolveApi!: (res: Response) => void;
    fetchMock.mockReturnValue(
      new Promise<Response>((resolve) => {
        resolveApi = resolve;
      })
    );

    render(
      <FollowButton
        targetUserId={42}
        initialFollowing={false}
        initialFollowersCount={10}
        showCount={true}
      />
    );

    const button = screen.getByRole("button", { name: /follow/i });
    await actor.click(button);

    // Optimistically updated before network response
    expect(button).toHaveTextContent("Following");
    expect(button).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByText("11")).toBeInTheDocument();

    // Settle network response
    const mockResponse: FollowToggleResponse = {
      following: true,
      followers_count: 11,
      following_count: 3,
    };
    resolveApi(respond(mockResponse, 200));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/users/42/follow"),
        expect.objectContaining({ method: "POST" })
      );
    });
  });

  // --- AC6: Optimistic toggle from followed to unfollowed ---
  it("optimistically updates to 'Follow' and decrements count on unfollow click (AC6)", async () => {
    const actor = userEvent.setup();
    let resolveApi!: (res: Response) => void;
    fetchMock.mockReturnValue(
      new Promise<Response>((resolve) => {
        resolveApi = resolve;
      })
    );

    render(
      <FollowButton
        targetUserId={42}
        initialFollowing={true}
        initialFollowersCount={10}
        showCount={true}
      />
    );

    const button = screen.getByRole("button", { name: /following/i });
    await actor.click(button);

    // Optimistically updated
    expect(button).toHaveTextContent("Follow");
    expect(button).toHaveAttribute("aria-pressed", "false");
    expect(screen.getByText("9")).toBeInTheDocument();

    // Settle
    resolveApi(respond({ following: false, followers_count: 9, following_count: 3 }, 200));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  });

  // --- AC7: Hovering over 'Following' shows 'Unfollow' text ---
  it("displays 'Unfollow' when hovering over a followed button (AC7)", async () => {
    const actor = userEvent.setup();
    render(<FollowButton targetUserId={42} initialFollowing={true} />);

    const button = screen.getByRole("button", { name: /following/i });
    expect(button).toHaveTextContent("Following");

    await actor.hover(button);
    expect(button).toHaveTextContent("Unfollow");

    await actor.unhover(button);
    expect(button).toHaveTextContent("Following");
  });

  // --- AC8: API error rollbacks optimistic state and renders alert ---
  it("rolls back optimistic changes and displays an error alert when API call fails (AC8)", async () => {
    const actor = userEvent.setup();
    fetchMock.mockResolvedValueOnce(
      respond({ detail: "Database connection failed" }, 500)
    );

    render(
      <FollowButton
        targetUserId={42}
        initialFollowing={false}
        initialFollowersCount={5}
        showCount={true}
      />
    );

    const button = screen.getByRole("button", { name: /follow/i });
    await actor.click(button);

    // After failure, it rolls back
    await waitFor(() => {
      expect(button).toHaveTextContent("Follow");
      expect(button).toHaveAttribute("aria-pressed", "false");
      expect(screen.getByText("5")).toBeInTheDocument();
      expect(screen.getByRole("alert")).toHaveTextContent("Database connection failed");
    });
  });

  // --- AC9: onToggle callback execution ---
  it("invokes onToggle callback with final follow status and follower count (AC9)", async () => {
    const actor = userEvent.setup();
    const handleToggle = vi.fn();
    fetchMock.mockResolvedValueOnce(
      respond({ following: true, followers_count: 100, following_count: 5 }, 200)
    );

    render(
      <FollowButton
        targetUserId={42}
        initialFollowing={false}
        onToggle={handleToggle}
      />
    );

    const button = screen.getByRole("button", { name: /follow/i });
    await actor.click(button);

    await waitFor(() => {
      expect(handleToggle).toHaveBeenCalledWith(42, true, 100);
    });
  });

  // --- AC10: Respects disabled prop and prevents in-flight double submission ---
  it("does not fire API requests when disabled (AC10)", async () => {
    const actor = userEvent.setup();
    render(<FollowButton targetUserId={42} initialFollowing={false} disabled={true} />);

    const button = screen.getByRole("button", { name: /follow/i });
    expect(button).toBeDisabled();

    await actor.click(button);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("prevents double-click duplicate requests while a request is pending (AC10)", async () => {
    const actor = userEvent.setup();
    let resolveApi!: (res: Response) => void;
    fetchMock.mockReturnValue(
      new Promise<Response>((resolve) => {
        resolveApi = resolve;
      })
    );

    render(<FollowButton targetUserId={42} initialFollowing={false} />);

    const button = screen.getByRole("button", { name: /follow/i });
    await actor.click(button);
    await actor.click(button); // Rapid second click

    expect(fetchMock).toHaveBeenCalledTimes(1);

    resolveApi(respond({ following: true, followers_count: 1, following_count: 0 }, 200));
    await waitFor(() => expect(button).toHaveTextContent("Following"));
  });
});
