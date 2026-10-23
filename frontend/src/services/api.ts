const API_URL = import.meta.env.VITE_API_URL ?? "";
const TOKEN_KEY = "simmer_token";
export const SESSION_EXPIRED = "simmer:session-expired";

// --- US1.1, US1.2, US1.3: User Profile & Authentication Data Model ---
export interface User {
  id: number;
  username: string;
  email: string;
  role: "user" | "admin";
  is_active: boolean;
  bio: string | null;
  avatar_url: string | null;
  culinary_preferences: string[];
  created_at: string;
}

export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

// --- US1.1: User Account Registration & Login (Local Token Persistence) ---
export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (token: string) => localStorage.setItem(TOKEN_KEY, token),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

// --- US1.1: HTTP Request Interceptor with Bearer Token & Session Handling ---
async function request<T>(path: string, options: RequestInit = {}, authenticated = true): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body) headers.set("Content-Type", "application/json");
  const token = authenticated ? tokenStore.get() : null;
  if (token) headers.set("Authorization", "Bearer " + token);
  const res = await fetch(API_URL + path, { ...options, headers });
  if (res.status === 204) return undefined as T;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    if (res.status === 401 && token) {
      tokenStore.clear();
      window.dispatchEvent(new Event(SESSION_EXPIRED));
    }
    const detail = data?.detail;
    const message = Array.isArray(detail)
      ? detail.map((d: { loc: string[]; msg: string }) => d.loc.at(-1) + ": " + d.msg).join("; ")
      : detail ?? "Request failed (" + res.status + ")";
    throw new ApiError(res.status, message);
  }
  return data as T;
}

const json = (body: unknown) => JSON.stringify(body);

export const api = {
  // --- US1.1: User Account Registration & Login Endpoints ---
  register: (email: string, username: string, password: string) =>
    request<User>("/api/v1/auth/register", { method: "POST", body: json({ email, username, password }) }, false),
  login: (username_or_email: string, password: string) =>
    request<{ access_token: string; user: User }>("/api/v1/auth/login", {
      method: "POST", body: json({ username_or_email, password }),
    }, false),
  me: () => request<User>("/api/v1/auth/me"),
};

export const errorText = (e: unknown) => e instanceof Error ? e.message : "Something went wrong";
