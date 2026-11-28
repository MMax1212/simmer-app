import { test, expect } from "@playwright/test";

// A fresh test database lets this verify the actual backend's cold-start contract,
// rather than a hand-written response that might misidentify fallback in production.
test("new users get fresh/community picks and a working preference setup link", async ({
  page, request,
}) => {
  await page.goto("/");
  const trending = page.getByRole("region", { name: "Trending Recipes This Week" });
  await expect(trending.getByText("No recipes to discover yet.")).toBeVisible();
  await expect(trending.getByRole("link", { name: "Share a recipe" })).toBeVisible();
  const base = "http://127.0.0.1:8001/api/v1";
  const username = `newcook_${Date.now()}`;
  const password = "test-password-123";
  expect((await request.post(`${base}/auth/register`, { data: {
    username, email: `${username}@example.com`, password,
  } })).ok()).toBe(true);
  const login = await request.post(`${base}/auth/login`, {
    data: { username_or_email: username, password },
  });
  const { access_token: token } = await login.json();
  // A recipe without engagement must appear as a fresh pick, never a scored trend.
  expect((await request.post(`${base}/recipes`, {
    headers: { Authorization: `Bearer ${token}` }, data: {
      title: "First community recipe", cuisine: "Italian",
      ingredients: [{ name: "Rice", amount: 1, unit: "cup" }],
      steps: [{ step_number: 1, instruction: "Cook the rice" }],
    },
  })).ok()).toBe(true);
  await page.evaluate((value) => localStorage.setItem("simmer_token", value), token);
  await page.reload();
  await expect(trending.getByText("Fresh picks", { exact: true })).toBeVisible();
  const recommended = page.getByRole("region", { name: "Recommended for You" });
  await expect(recommended.getByText("Community picks", { exact: true })).toBeVisible();
  await expect(recommended.getByRole("link", { name: /First community recipe/ })).toBeVisible();
  await recommended.getByRole("link", { name: "Choose your preferences" }).click();
  await expect(page).toHaveURL(/\/profile$/);
});
