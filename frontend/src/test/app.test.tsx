import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "../App";
import { recipe, user } from "./fixtures";

const respond = (data: unknown, status = 200) => new Response(JSON.stringify(data), {
  status, headers: { "Content-Type": "application/json" },
});

const fetchMock = vi.fn<typeof fetch>();

beforeEach(() => {
  vi.stubGlobal("fetch", fetchMock);
  fetchMock.mockReset();
});

function open(path: string, signedIn = false) {
  window.history.replaceState(null, "", path);
  if (signedIn) localStorage.setItem("simmer_token", "valid-token");
  render(<App />);
}

describe("authentication", () => {
  // --- US1.1: User Account Registration & Login (Client-Side Validation on Submit) ---
  it("rejects invalid registration without sending a request", async () => {
    const actor = userEvent.setup();
    open("/register");
    await actor.type(screen.getByLabelText("Email"), "bad-email");
    await actor.type(screen.getByLabelText("Username"), "ana");
    await actor.type(screen.getByLabelText("Password", { exact: true }), "password123");
    await actor.type(screen.getByLabelText("Confirm password"), "password123");
    await actor.click(screen.getByRole("button", { name: "Sign up" }));
    expect(fetchMock).not.toHaveBeenCalled();
    expect(screen.getByLabelText("Email")).toBeInvalid();
  });

  // --- US1.1: User Account Registration & Login (Client-Side Password Match Check) ---
  it("shows mismatched password errors before calling the API", async () => {
    const actor = userEvent.setup();
    open("/register");
    await actor.type(screen.getByLabelText("Email"), "ana@example.com");
    await actor.type(screen.getByLabelText("Username"), "ana");
    await actor.type(screen.getByLabelText("Password", { exact: true }), "password123");
    await actor.type(screen.getByLabelText("Confirm password"), "different123");
    await actor.click(screen.getByRole("button", { name: "Sign up" }));
    expect(await screen.findByText("Passwords don't match")).toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  // --- US1.1 & US1.5: Successful Login & Redirect to "My Recipes" Library ---
  it("logs in using a username, stores the token and opens My Recipes", async () => {
    fetchMock.mockImplementation(async (url) =>
      String(url).includes("/auth/login") ? respond({ access_token: "new-token", user }) : respond([]));
    const actor = userEvent.setup();
    open("/login");
    await actor.type(screen.getByLabelText("Username or email"), "ana");
    await actor.type(screen.getByLabelText("Password"), "password123");
    await actor.click(screen.getByRole("button", { name: "Log in" }));
    expect(await screen.findByRole("heading", { name: "My Recipes" })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/recipes/my-recipes");
    expect(localStorage.getItem("simmer_token")).toBe("new-token");
    expect(JSON.parse(fetchMock.mock.calls[0][1]!.body as string)).toEqual({
      username_or_email: "ana", password: "password123",
    });
    expect(await screen.findByText("No recipes yet.", { exact: false })).toBeInTheDocument();
  });

  // --- US1.1: Session Management (Expired Token Cleared & Redirect to Login) ---
  it("clears an expired session and redirects to login", async () => {
    fetchMock.mockImplementation(async (url) => String(url).endsWith("/auth/me")
      ? respond(user) : respond({ detail: "Invalid or expired token" }, 401));
    open("/recipes/my-recipes", true);
    expect(await screen.findByRole("heading", { name: "Log in" })).toBeInTheDocument();
    expect(localStorage.getItem("simmer_token")).toBeNull();
    expect(screen.queryByRole("button", { name: "Log out" })).not.toBeInTheDocument();
  });

  // --- US1.2: Admin Account & RBAC (Unauthorized Access to Admin Route Blocked) ---
  it("prevents ordinary users opening the admin screen", async () => {
    fetchMock.mockResolvedValue(respond(user));
    open("/admin", true);
    await waitFor(() => expect(window.location.pathname).toBe("/"));
    expect(fetchMock.mock.calls.every(([url]) => !String(url).includes("/admin/users"))).toBe(true);
  });
});
