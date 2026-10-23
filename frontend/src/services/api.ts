const API_URL = import.meta.env.VITE_API_URL ?? "";
const TOKEN_KEY = "simmer_token";
export const SESSION_EXPIRED = "simmer:session-expired";

export const CULINARY_PREFS = [
  "Italian", "Mexican", "Vegan", "Quick & Easy", "Baking",
  "vegetarian", "vegan", "pescatarian", "gluten-free", "dairy-free",
  "nut-free", "halal", "kosher", "low-carb",
];

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

export interface Ingredient {
  id?: number;
  name: string;
  amount: number | null;
  unit: string | null;
}

export interface RecipeStep {
  id?: number;
  step_number: number;
  instruction: string;
}

export interface RecipeInput {
  title: string;
  description: string | null;
  cuisine: string | null;
  meal_type: string | null;
  difficulty: "easy" | "medium" | "hard";
  image_url: string | null;
  prep_time_mins: number;
  cook_time_mins: number;
  servings: number;
  ingredients: Ingredient[];
  steps: RecipeStep[];
}

export interface Recipe extends RecipeInput {
  id: number;
  author_id: number;
  author_username: string;
  created_at: string;
  updated_at: string;
}

export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (token: string) => localStorage.setItem(TOKEN_KEY, token),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

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
  register: (email: string, username: string, password: string) =>
    request<User>("/api/v1/auth/register", { method: "POST", body: json({ email, username, password }) }, false),
  login: (username_or_email: string, password: string) =>
    request<{ access_token: string; user: User }>("/api/v1/auth/login", {
      method: "POST", body: json({ username_or_email, password }),
    }, false),
  me: () => request<User>("/api/v1/auth/me"),
  updateProfile: (changes: Partial<Pick<User, "bio" | "avatar_url" | "culinary_preferences">>) =>
    request<User>("/api/v1/users/me", { method: "PUT", body: json(changes) }),
  myRecipes: (offset = 0, limit = 20) =>
    request<Recipe[]>("/api/v1/recipes/my-recipes?offset=" + offset + "&limit=" + limit),
  getRecipe: (id: number) => request<Recipe>("/api/v1/recipes/" + id),
  createRecipe: (recipe: RecipeInput) =>
    request<Recipe>("/api/v1/recipes", { method: "POST", body: json(recipe) }),
  updateRecipe: (id: number, recipe: RecipeInput) =>
    request<Recipe>("/api/v1/recipes/" + id, { method: "PUT", body: json(recipe) }),
  deleteRecipe: (id: number) => request<void>("/api/v1/recipes/" + id, { method: "DELETE" }),
  adminListUsers: () => request<User[]>("/api/v1/admin/users"),
  adminUpdateUser: (id: number, changes: { is_active?: boolean; role?: string }) =>
    request<User>("/api/v1/admin/users/" + id + "/status", { method: "PATCH", body: json(changes) }),
};

export const errorText = (e: unknown) => e instanceof Error ? e.message : "Something went wrong";
