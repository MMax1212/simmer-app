// Thin wrapper around fetch for the Simmer API.
// Base URL comes from frontend/.env (VITE_API_URL), defaulting to the local backend.
const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const TOKEN_KEY = "simmer_token";

export const DIETARY_PREFS = [
  "vegetarian", "vegan", "pescatarian", "gluten-free", "dairy-free",
  "nut-free", "halal", "kosher", "low-carb",
] as const;

export interface User {
  id: number;
  username: string;
  email: string;
  role: "user" | "admin";
  is_active: boolean;
  bio: string | null;
  avatar_url: string | null;
  dietary_prefs: string[];
  created_at: string;
}

export interface Ingredient {
  id?: number;
  name: string;
  quantity: number | null;
  unit: string | null;
}

export interface RecipeInput {
  title: string;
  description: string | null;
  instructions: string;
  prep_time_mins: number | null;
  cook_time_mins: number | null;
  servings: number | null;
  ingredients: Ingredient[];
}

export interface Recipe extends RecipeInput {
  id: number;
  owner_id: number;
  owner_username: string;
  created_at: string;
  updated_at: string;
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export const tokenStore = {
  // localStorage is simple but readable by any script on the page; fine for a class project.
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (t: string) => localStorage.setItem(TOKEN_KEY, t),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body) headers.set("Content-Type", "application/json");
  const token = tokenStore.get();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (res.status === 204) return undefined as T;

  const data = await res.json().catch(() => null);
  if (!res.ok) {
    // FastAPI returns {detail: "msg"} or, for validation errors, {detail: [{msg, loc}, ...]}
    const detail = data?.detail;
    const message = Array.isArray(detail)
      ? detail.map((d: { loc: string[]; msg: string }) => `${d.loc.at(-1)}: ${d.msg}`).join("; ")
      : detail ?? `Request failed (${res.status})`;
    throw new ApiError(res.status, message);
  }
  return data as T;
}

const json = (body: unknown) => JSON.stringify(body);

export const api = {
  register: (email: string, username: string, password: string) =>
    request<User>("/api/auth/register", { method: "POST", body: json({ email, username, password }) }),
  login: (email: string, password: string) =>
    request<{ access_token: string }>("/api/auth/login", { method: "POST", body: json({ email, password }) }),
  me: () => request<User>("/api/users/me"),
  updateProfile: (changes: Partial<Pick<User, "bio" | "avatar_url" | "dietary_prefs">>) =>
    request<User>("/api/users/me", { method: "PATCH", body: json(changes) }),

  myRecipes: () => request<Recipe[]>("/api/users/me/recipes"),
  getRecipe: (id: number) => request<Recipe>(`/api/recipes/${id}`),
  createRecipe: (r: RecipeInput) => request<Recipe>("/api/recipes", { method: "POST", body: json(r) }),
  updateRecipe: (id: number, r: RecipeInput) =>
    request<Recipe>(`/api/recipes/${id}`, { method: "PUT", body: json(r) }),
  deleteRecipe: (id: number) => request<void>(`/api/recipes/${id}`, { method: "DELETE" }),

  adminListUsers: () => request<User[]>("/api/admin/users"),
  adminUpdateUser: (id: number, changes: { is_active?: boolean; role?: string }) =>
    request<User>(`/api/admin/users/${id}`, { method: "PATCH", body: json(changes) }),
};

export const errorText = (e: unknown) => (e instanceof Error ? e.message : "Something went wrong");
