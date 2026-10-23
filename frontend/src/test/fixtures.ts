import type { Recipe, User } from "../services/api";

// --- US1.1, US1.2 & US1.3: Mock User Test Fixture ---
export const user: User = {
  id: 1, username: "ana", email: "ana@example.com", role: "user", is_active: true,
  bio: null, avatar_url: null, culinary_preferences: [], created_at: "2026-10-12",
};