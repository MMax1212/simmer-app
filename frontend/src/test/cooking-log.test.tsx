import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "../App";
import { recipe, user } from "./fixtures";

const path = `/api/v1/recipes/${recipe.id}/complete`;
const fetchMock = vi.fn<typeof fetch>();
const response = (body: unknown, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { "Content-Type": "application/json" },
});
const completed = { id: 104, recipe_id: recipe.id, user_id: user.id,
  cooked_at: "2026-11-02T12:00:00Z", notes: null, rating: null };
const submissions = () => fetchMock.mock.calls.filter(([url, init]) =>
  String(url) === path && init?.method === "POST");

beforeEach(() => {
  vi.stubGlobal("fetch", fetchMock);
  fetchMock.mockReset();
  // Reject unexpected routes instead of silently returning an unrelated fixture.
  fetchMock.mockImplementation(async (url, init) => {
    if (String(url) === "/api/v1/auth/me") return response(user);
    if (String(url) === `/api/v1/recipes/${recipe.id}`) return response(recipe);
    if (String(url) === path && init?.method === "POST") return response(completed, 201);
    throw new Error(`Unexpected request: ${init?.method ?? "GET"} ${url}`);
  });
});

async function openRecipe(signedIn = true) {
  window.history.replaceState(null, "", `/recipes/${recipe.id}`);
  if (signedIn) localStorage.setItem("simmer_token", "valid-token");
  render(<App />);
  await screen.findByRole("heading", { name: recipe.title });
  if (signedIn) await screen.findByRole("button", { name: "Log out" });
}
async function openLog() {
  const actor = userEvent.setup();
  await openRecipe();
  await actor.click(screen.getByRole("button", { name: /i cooked this/i }));
  return { actor, dialog: screen.getByRole("dialog", { name: /i cooked this/i }) };
}

// US2.3 red-phase tests specify observable behavior and accessible labels.
// The approved completion body contains notes/rating; custom cooked dates need
// an agreed backend contract before tests can dictate date submission behavior.
describe("US2.3 cooking-log behavior", () => {
  it("opens a named dialog and cancels without recording an event", async () => {
    const { actor, dialog } = await openLog();
    await actor.type(within(dialog).getByLabelText(/notes/i), "Trying this recipe");
    await actor.click(within(dialog).getByRole("button", { name: /cancel/i }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(submissions()).toHaveLength(0);
  });

  it("records an event without requiring notes or a rating", async () => {
    const { actor, dialog } = await openLog();
    await actor.click(within(dialog).getByRole("button", { name: /save cooking log/i }));
    await waitFor(() => expect(submissions()).toHaveLength(1));
    const [, init] = submissions()[0];
    const body = JSON.parse(init!.body as string);
    // Optional fields may be omitted or sent as null, but never invented values.
    expect(body.notes ?? null).toBeNull();
    expect(body.rating ?? null).toBeNull();
    expect(new Headers(init!.headers).get("Authorization")).toBe("Bearer valid-token");
    expect(await screen.findByRole("status")).toHaveTextContent(/saved to cooking history/i);
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("submits optional notes and a five-star rating", async () => {
    const { actor, dialog } = await openLog();
    await actor.type(within(dialog).getByLabelText(/notes/i), "Added extra basil");
    await actor.click(within(dialog).getByRole("radio", { name: /5 stars/i }));
    await actor.click(within(dialog).getByRole("button", { name: /save cooking log/i }));
    await waitFor(() => expect(submissions()).toHaveLength(1));
    expect(JSON.parse(submissions()[0][1]!.body as string)).toEqual({ notes: "Added extra basil", rating: 5 });
  });

  it("preserves notes and permits retry when saving fails", async () => {
    const { actor, dialog } = await openLog();
    await actor.type(within(dialog).getByLabelText(/notes/i), "Try less salt next time");
    fetchMock.mockResolvedValueOnce(response({ detail: "Unable to save cooking log" }, 500));
    await actor.click(within(dialog).getByRole("button", { name: /save cooking log/i }));
    expect(await within(dialog).findByRole("alert")).toHaveTextContent("Unable to save cooking log");
    expect(within(dialog).getByLabelText(/notes/i)).toHaveValue("Try less salt next time");
    const retry = within(dialog).getByRole("button", { name: /save cooking log/i });
    expect(retry).toBeEnabled();
    await actor.click(retry);
    expect(await screen.findByRole("status")).toHaveTextContent(/saved to cooking history/i);
    expect(submissions()).toHaveLength(2);
  });

  it("prevents rapid double clicks from sending duplicate submissions", async () => {
    const { actor, dialog } = await openLog();
    let finish!: (value: Response) => void;
    fetchMock.mockReturnValueOnce(new Promise<Response>((resolve) => { finish = resolve; }));
    try {
      const save = within(dialog).getByRole("button", { name: /save cooking log/i });
      await actor.dblClick(save);
      expect(submissions()).toHaveLength(1);
      expect(save).toBeDisabled();
    } finally {
      // Always release the simulated request, including when assertions fail.
      finish(response(completed, 201));
    }
    expect(await screen.findByRole("status")).toHaveTextContent(/saved to cooking history/i);
  });

  it("does not offer authenticated submission to signed-out visitors", async () => {
    await openRecipe(false);
    expect(screen.queryByRole("button", { name: /i cooked this/i })).not.toBeInTheDocument();
    expect(submissions()).toHaveLength(0);
  });
});
