import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "../App";
import { user } from "./fixtures";
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
    if (signedIn)
        localStorage.setItem("simmer_token", "valid-token");
    render(<App />);
}
describe("authentication", () => {
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
    it("logs in and opens the home screen", async () => {
        fetchMock.mockResolvedValue(respond({ access_token: "new-token", user }));
        const actor = userEvent.setup();
        open("/login");
        await actor.type(screen.getByLabelText("Username or email"), "ana");
        await actor.type(screen.getByLabelText("Password"), "password123");
        await actor.click(screen.getByRole("button", { name: "Log in" }));
        expect(await screen.findByRole("heading", { name: "Welcome back, ana" })).toBeInTheDocument();
        expect(window.location.pathname).toBe("/");
        expect(localStorage.getItem("simmer_token")).toBe("new-token");
    });
    it("clears an expired session and redirects to login", async () => {
        fetchMock.mockImplementation(async (url) => String(url).endsWith("/auth/me")
            ? respond({ ...user, role: "admin" }) : respond({ detail: "Invalid or expired token" }, 401));
        open("/admin", true);
        expect(await screen.findByRole("heading", { name: "Log in" })).toBeInTheDocument();
        expect(localStorage.getItem("simmer_token")).toBeNull();
        expect(screen.queryByRole("button", { name: "Log out" })).not.toBeInTheDocument();
    });
    it("prevents ordinary users opening the admin screen", async () => {
        fetchMock.mockResolvedValue(respond(user));
        open("/admin", true);
        await waitFor(() => expect(window.location.pathname).toBe("/"));
        expect(fetchMock.mock.calls.every(([url]) => !String(url).includes("/admin/users"))).toBe(true);
    });
});
describe("admin management", () => {
    it("lets admins deactivate/reactivate accounts and update roles", async () => {
        const admin = { ...user, id: 2, username: "boss", role: "admin" as const };
        fetchMock.mockImplementation(async (url, init) => {
            if (String(url).endsWith("/auth/me"))
                return respond(admin);
            if (init?.method === "PATCH")
                return respond({ ...user, ...JSON.parse(init.body as string) });
            return respond([user, admin]);
        });
        const actor = userEvent.setup();
        open("/admin", true);
        await actor.click(await screen.findByRole("button", { name: "Deactivate" }));
        await actor.click(await screen.findByRole("button", { name: "Reactivate" }));
        await actor.selectOptions(screen.getByLabelText("Role for ana"), "admin");
        await waitFor(() => expect(screen.getByLabelText("Role for ana")).toHaveValue("admin"));
        expect(fetchMock.mock.calls.filter(([, init]) => init?.method === "PATCH").map(([, init]) => JSON.parse(init!.body as string)))
            .toEqual([{ is_active: false }, { is_active: true }, { role: "admin" }]);
        expect(screen.queryByLabelText("Role for boss")).not.toBeInTheDocument();
    });
});
