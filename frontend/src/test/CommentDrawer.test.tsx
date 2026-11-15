import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { CommentDrawer } from "../components/CommentDrawer";
import {
  api,
  createPostComment,
  getPostComments,
  tokenStore,
  type Comment,
} from "../services/api";

const respond = (data: unknown, status = 200) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });

const fetchMock = vi.fn<typeof fetch>();

const sampleComments: Comment[] = [
  {
    id: 1,
    post_id: 10,
    user_id: 2,
    username: "chef_mario",
    avatar_url: null,
    content: "Looks delicious! Did you use fresh basil?",
    created_at: "2026-11-14T10:00:00Z",
  },
  {
    id: 2,
    post_id: 10,
    user_id: 3,
    username: "baker_lucy",
    avatar_url: "https://example.com/avatar.jpg",
    content: "Saved this to try over the weekend!",
    created_at: "2026-11-14T11:30:00Z",
  },
];

beforeEach(() => {
  vi.stubGlobal("fetch", fetchMock);
  fetchMock.mockReset();
  localStorage.clear();
});

describe("US3.3.5: Slide-Out Comment Thread Drawer Component", () => {
  // --- AC1: Dialog visibility ---
  it("US3.3.5 renders drawer dialog when isOpen is true (AC1)", async () => {
    fetchMock.mockResolvedValue(respond([]));
    render(<CommentDrawer postId={10} isOpen={true} onClose={vi.fn()} />);

    const dialog = screen.getByRole("dialog");
    expect(dialog).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /comments/i })).toBeInTheDocument();
  });

  it("US3.3.5 does not render dialog when isOpen is false (AC1)", () => {
    render(<CommentDrawer postId={10} isOpen={false} onClose={vi.fn()} />);

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  // --- AC2: Close interactions ---
  it("US3.3.5 invokes onClose when clicking close button, backdrop, or pressing Escape (AC2)", async () => {
    const actor = userEvent.setup();
    const onClose = vi.fn();
    fetchMock.mockResolvedValue(respond([]));

    render(<CommentDrawer postId={10} isOpen={true} onClose={onClose} />);

    // Click close button
    const closeBtn = screen.getByRole("button", { name: /close comments/i });
    await actor.click(closeBtn);
    expect(onClose).toHaveBeenCalledTimes(1);

    // Backdrop click
    const backdrop = screen.getByTestId("drawer-backdrop");
    await actor.click(backdrop);
    expect(onClose).toHaveBeenCalledTimes(2);

    // Escape key press
    await actor.keyboard("{Escape}");
    expect(onClose).toHaveBeenCalledTimes(3);
  });

  // --- AC3: Fetch and render comments ---
  it("US3.3.5 fetches and renders comments on open from GET /api/v1/posts/:id/comments (AC3)", async () => {
    fetchMock.mockResolvedValue(respond(sampleComments));

    render(<CommentDrawer postId={10} isOpen={true} onClose={vi.fn()} />);

    expect(await screen.findByText("Looks delicious! Did you use fresh basil?")).toBeInTheDocument();
    expect(screen.getByText("Saved this to try over the weekend!")).toBeInTheDocument();
    expect(screen.getByText("chef_mario")).toBeInTheDocument();
    expect(screen.getByText("baker_lucy")).toBeInTheDocument();

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/posts/10/comments"),
      expect.anything()
    );
  });

  // --- AC4: Empty state message ---
  it("US3.3.5 renders empty state message when a post has zero comments (AC4)", async () => {
    fetchMock.mockResolvedValue(respond([]));

    render(<CommentDrawer postId={10} isOpen={true} onClose={vi.fn()} />);

    expect(
      await screen.findByText(/no comments yet\. be the first to share your thoughts!/i)
    ).toBeInTheDocument();
  });

  // --- AC5: Input validation & character counter ---
  it("US3.3.5 disables submit button for empty/whitespace input and enforces 1,000 char limit (AC5)", async () => {
    const actor = userEvent.setup();
    fetchMock.mockResolvedValue(respond([]));

    render(<CommentDrawer postId={10} isOpen={true} onClose={vi.fn()} />);

    const submitBtn = screen.getByRole("button", { name: /post/i });
    expect(submitBtn).toBeDisabled();

    const input = screen.getByPlaceholderText(/add a comment\.\.\./i);
    await actor.type(input, "   ");
    expect(submitBtn).toBeDisabled();

    await actor.clear(input);
    await actor.type(input, "Great tip!");
    expect(submitBtn).toBeEnabled();
    expect(screen.getByText(/10\s*\/\s*1000/)).toBeInTheDocument();
  });

  // --- AC6: Dispatches authenticated POST request ---
  it("US3.3.5 dispatches authenticated POST /api/v1/posts/:id/comments on submit (AC6)", async () => {
    const actor = userEvent.setup();
    tokenStore.set("auth-token-xyz");

    const newComment: Comment = {
      id: 99,
      post_id: 10,
      user_id: 1,
      username: "current_user",
      avatar_url: null,
      content: "Amazing recipe!",
      created_at: "2026-11-14T12:00:00Z",
    };

    fetchMock
      .mockResolvedValueOnce(respond([]))
      .mockResolvedValueOnce(respond(newComment, 201));

    render(<CommentDrawer postId={10} isOpen={true} onClose={vi.fn()} />);

    const input = screen.getByPlaceholderText(/add a comment\.\.\./i);
    await actor.type(input, "Amazing recipe!");
    await actor.click(screen.getByRole("button", { name: /post/i }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/posts/10/comments"),
        expect.objectContaining({
          method: "POST",
          headers: expect.any(Headers),
          body: JSON.stringify({ content: "Amazing recipe!" }),
        })
      );
    });

    const callHeaders = fetchMock.mock.calls[1][1]?.headers as Headers;
    expect(callHeaders.get("Authorization")).toBe("Bearer auth-token-xyz");
  });

  // --- AC7: Optimistic update ---
  it("US3.3.5 optimistically displays comment immediately upon submission (AC7)", async () => {
    const actor = userEvent.setup();
    let resolvePost: (res: Response) => void;

    fetchMock
      .mockResolvedValueOnce(respond([]))
      .mockReturnValueOnce(
        new Promise<Response>((resolve) => {
          resolvePost = resolve;
        })
      );

    render(<CommentDrawer postId={10} isOpen={true} onClose={vi.fn()} />);

    const input = screen.getByPlaceholderText(/add a comment\.\.\./i);
    await actor.type(input, "Immediate feedback comment!");
    await actor.click(screen.getByRole("button", { name: /post/i }));

    // Immediately rendered before resolvePost finishes
    expect(screen.getByText("Immediate feedback comment!")).toBeInTheDocument();
    // Input is cleared
    expect(input).toHaveValue("");

    resolvePost!(
      respond({
        id: 100,
        post_id: 10,
        user_id: 1,
        username: "current_user",
        avatar_url: null,
        content: "Immediate feedback comment!",
        created_at: "2026-11-14T12:00:00Z",
      }, 201)
    );
  });

  // --- AC8: Error rollback ---
  it("US3.3.5 rolls back optimistic comment and restores input on API failure (AC8)", async () => {
    const actor = userEvent.setup();
    fetchMock
      .mockResolvedValueOnce(respond([]))
      .mockResolvedValueOnce(respond({ detail: "Comment submission failed" }, 500));

    render(<CommentDrawer postId={10} isOpen={true} onClose={vi.fn()} />);

    const input = screen.getByPlaceholderText(/add a comment\.\.\./i);
    await actor.type(input, "This will fail");
    await actor.click(screen.getByRole("button", { name: /post/i }));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toBeInTheDocument();
    });

    // Optimistic comment removed from comment thread
    const commentList = screen.getByTestId("comments-list");
    expect(within(commentList).queryByText("This will fail")).not.toBeInTheDocument();
    // Input restored
    expect(input).toHaveValue("This will fail");
  });

  // --- API Client Helpers ---
  it("US3.3.5 getPostComments and createPostComment API client helpers invoke expected endpoints", async () => {
    tokenStore.set("test-token");
    fetchMock.mockImplementation(() => Promise.resolve(respond(sampleComments)));

    const comments = await getPostComments(10);
    expect(comments).toEqual(sampleComments);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/posts/10/comments"),
      expect.anything()
    );

    const fromApi = await api.getPostComments(10);
    expect(fromApi).toEqual(sampleComments);

    const created: Comment = {
      id: 5,
      post_id: 10,
      user_id: 1,
      username: "user1",
      avatar_url: null,
      content: "Nice!",
      created_at: "2026-11-14T12:00:00Z",
    };
    fetchMock.mockImplementation(() => Promise.resolve(respond(created, 201)));

    const posted = await createPostComment(10, "Nice!");
    expect(posted).toEqual(created);

    const postedFromApi = await api.createPostComment(10, "Nice!");
    expect(postedFromApi).toEqual(created);
  });
});
