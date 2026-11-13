import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { LikeButton } from "../components/LikeButton";
import { api, togglePostLike, tokenStore, type LikeToggleResponse } from "../services/api";

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

describe("US3.3.4: Interactive Heart Like Button Component", () => {
  // --- AC1: Initial visual state and count ---
  it("US3.3.4 renders with correct initial visual state and count when unliked (AC1)", () => {
    render(<LikeButton postId={101} initialLiked={false} initialLikesCount={5} />);

    const button = screen.getByRole("button", { name: "Like post" });
    expect(button).toBeInTheDocument();
    expect(button).toHaveAttribute("aria-pressed", "false");
    expect(screen.getByText("5")).toBeInTheDocument();

    const heartIcon = button.querySelector("svg");
    expect(heartIcon).toBeInTheDocument();
    expect(heartIcon).not.toHaveClass("fill-rose-500");
  });

  it("US3.3.4 renders with correct initial visual state and count when liked (AC1)", () => {
    render(<LikeButton postId={101} initialLiked={true} initialLikesCount={12} />);

    const button = screen.getByRole("button", { name: "Unlike post" });
    expect(button).toBeInTheDocument();
    expect(button).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByText("12")).toBeInTheDocument();

    const heartIcon = button.querySelector("svg");
    expect(heartIcon).toBeInTheDocument();
    expect(heartIcon).toHaveClass("fill-rose-500");
    expect(heartIcon).toHaveClass("text-rose-500");
  });

  // --- AC2: Optimistic update when unliked (+1 and filled red) ---
  it("US3.3.4 immediately flips heart to filled red and increments count by +1 on click when unliked (AC2)", async () => {
    const actor = userEvent.setup();
    let resolveApi: (res: Response) => void;
    fetchMock.mockReturnValue(
      new Promise<Response>((resolve) => {
        resolveApi = resolve;
      })
    );

    render(<LikeButton postId={101} initialLiked={false} initialLikesCount={4} />);

    const button = screen.getByRole("button", { name: "Like post" });
    await actor.click(button);

    // Immediate optimistic state before API resolution
    expect(screen.getByRole("button", { name: "Unlike post" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByText("5")).toBeInTheDocument();
    const heartIcon = screen.getByRole("button", { name: "Unlike post" }).querySelector("svg");
    expect(heartIcon).toHaveClass("fill-rose-500");

    // Clean up pending promise
    resolveApi!(respond({ liked: true, likes_count: 5 }));
  });

  // --- AC3: Optimistic update when liked (-1 and outline gray) ---
  it("US3.3.4 immediately flips heart to outline gray and decrements count by -1 on click when liked (AC3)", async () => {
    const actor = userEvent.setup();
    let resolveApi: (res: Response) => void;
    fetchMock.mockReturnValue(
      new Promise<Response>((resolve) => {
        resolveApi = resolve;
      })
    );

    render(<LikeButton postId={101} initialLiked={true} initialLikesCount={8} />);

    const button = screen.getByRole("button", { name: "Unlike post" });
    await actor.click(button);

    // Immediate optimistic state before API resolution
    expect(screen.getByRole("button", { name: "Like post" })).toHaveAttribute("aria-pressed", "false");
    expect(screen.getByText("7")).toBeInTheDocument();
    const heartIcon = screen.getByRole("button", { name: "Like post" }).querySelector("svg");
    expect(heartIcon).not.toHaveClass("fill-rose-500");

    // Clean up pending promise
    resolveApi!(respond({ liked: false, likes_count: 7 }));
  });

  // --- AC4: Dispatches authenticated POST request ---
  it("US3.3.4 dispatches authenticated POST /api/v1/posts/:id/like on click (AC4)", async () => {
    const actor = userEvent.setup();
    tokenStore.set("test-jwt-token");
    const mockResponse: LikeToggleResponse = { liked: true, likes_count: 1 };
    fetchMock.mockResolvedValue(respond(mockResponse));

    render(<LikeButton postId={42} initialLiked={false} initialLikesCount={0} />);

    await actor.click(screen.getByRole("button", { name: "Like post" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/posts/42/like"),
        expect.objectContaining({
          method: "POST",
          headers: expect.any(Headers),
        })
      );
    });

    // Verify Bearer token was forwarded in headers
    const calledHeaders = fetchMock.mock.calls[0][1]?.headers as Headers;
    expect(calledHeaders.get("Authorization")).toBe("Bearer test-jwt-token");
  });

  // --- AC5: Reconciles count with server response ---
  it("US3.3.4 finalizes state and count using server returned likes_count on HTTP 200 (AC5)", async () => {
    const actor = userEvent.setup();
    const onToggle = vi.fn();
    // Simulate server having a higher count due to concurrent likes from other users
    const mockResponse: LikeToggleResponse = { liked: true, likes_count: 15 };
    fetchMock.mockResolvedValue(respond(mockResponse));

    render(
      <LikeButton
        postId={101}
        initialLiked={false}
        initialLikesCount={3}
        onToggle={onToggle}
      />
    );

    await actor.click(screen.getByRole("button", { name: "Like post" }));

    await waitFor(() => {
      expect(screen.getByText("15")).toBeInTheDocument();
    });

    expect(onToggle).toHaveBeenCalledWith(101, true, 15);
  });

  // --- AC6: Error rollback ---
  it("US3.3.4 rolls back heart color and count to pre-click values on network or HTTP error (AC6)", async () => {
    const actor = userEvent.setup();
    const onToggle = vi.fn();
    fetchMock.mockResolvedValue(respond({ detail: "Server error" }, 500));

    render(
      <LikeButton
        postId={101}
        initialLiked={false}
        initialLikesCount={4}
        onToggle={onToggle}
      />
    );

    const button = screen.getByRole("button", { name: "Like post" });
    await actor.click(button);

    // Rolls back to initial state after error
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Like post" })).toHaveAttribute("aria-pressed", "false");
      expect(screen.getByText("4")).toBeInTheDocument();
    });

    // Callback should not be called with failed state
    expect(onToggle).not.toHaveBeenCalled();

    // Alert or error message is displayed
    expect(await screen.findByRole("alert")).toBeInTheDocument();
  });

  // --- AC7: Prevent duplicate concurrent requests ---
  it("US3.3.4 prevents duplicate concurrent requests while in-flight (AC7)", async () => {
    const actor = userEvent.setup();
    let resolveApi: (res: Response) => void;
    fetchMock.mockReturnValue(
      new Promise<Response>((resolve) => {
        resolveApi = resolve;
      })
    );

    render(<LikeButton postId={101} initialLiked={false} initialLikesCount={2} />);

    const button = screen.getByRole("button", { name: "Like post" });
    // Click twice rapidly
    await actor.click(button);
    await actor.click(button);

    expect(fetchMock).toHaveBeenCalledTimes(1);

    resolveApi!(respond({ liked: true, likes_count: 3 }));
  });

  // --- AC8: Keyboard accessibility & ARIA ---
  it("US3.3.4 supports keyboard activation with Enter and Space (AC8)", async () => {
    const actor = userEvent.setup();
    fetchMock.mockResolvedValue(respond({ liked: true, likes_count: 6 }));

    render(<LikeButton postId={101} initialLiked={false} initialLikesCount={5} />);

    const button = screen.getByRole("button", { name: "Like post" });
    button.focus();
    expect(button).toHaveFocus();

    await actor.keyboard("{Enter}");
    expect(screen.getByRole("button", { name: "Unlike post" })).toBeInTheDocument();
  });

  // --- Boundary & Disabled Guards ---
  it("US3.3.4 guards boundary count from dropping below zero", async () => {
    const actor = userEvent.setup();
    fetchMock.mockResolvedValue(respond({ liked: false, likes_count: 0 }));

    render(<LikeButton postId={101} initialLiked={true} initialLikesCount={0} />);

    await actor.click(screen.getByRole("button", { name: "Unlike post" }));

    expect(screen.getByText("0")).toBeInTheDocument();
  });

  it("US3.3.4 disables interaction when disabled prop is true", async () => {
    const actor = userEvent.setup();
    render(<LikeButton postId={101} initialLiked={false} initialLikesCount={3} disabled />);

    const button = screen.getByRole("button", { name: "Like post" });
    expect(button).toBeDisabled();

    await actor.click(button);
    expect(fetchMock).not.toHaveBeenCalled();
    expect(screen.getByText("3")).toBeInTheDocument();
  });

  // --- API Client Integration ---
  it("US3.3.4 togglePostLike API helper invokes POST /api/v1/posts/:id/like", async () => {
    tokenStore.set("auth-token-123");
    fetchMock.mockImplementation(() => Promise.resolve(respond({ liked: true, likes_count: 9 })));

    const res = await togglePostLike(77);
    expect(res).toEqual({ liked: true, likes_count: 9 });
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/posts/77/like"),
      expect.objectContaining({ method: "POST" })
    );

    const resFromApi = await api.togglePostLike(77);
    expect(resFromApi).toEqual({ liked: true, likes_count: 9 });
  });
});
