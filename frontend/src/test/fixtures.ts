import type { Recipe, User } from "../services/api";

export const user: User = {
  id: 1, username: "ana", email: "ana@example.com", role: "user", is_active: true,
  bio: null, avatar_url: null, culinary_preferences: [], created_at: "2026-10-12",
};

export const recipe: Recipe = {
  id: 1, author_id: 1, author_username: "ana", title: "Tomato Pasta", description: "Weeknight dinner",
  cuisine: "Italian", meal_type: "Dinner", difficulty: "easy", image_url: null,
  prep_time_mins: 10, cook_time_mins: 20, servings: 2,
  ingredients: [{ id: 10, name: "pasta", amount: 200, unit: "g" }],
  steps: [{ id: 20, step_number: 1, instruction: "Boil the pasta" }],
  created_at: "2026-10-12", updated_at: "2026-10-12",
};
