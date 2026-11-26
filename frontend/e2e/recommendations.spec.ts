import { test, expect } from "@playwright/test";

// Unlike mocked card tests, this exercises stored preferences through the real API
// and verifies that logout removes private discovery while public trending remains.
test("Home recommendations follow saved preferences and disappear on logout", async ({
  page, request,
}) => {
  const base = "http://127.0.0.1:8001/api/v1";
  const username = `recommend_${Date.now()}`;
  const password = "test-password-123";
  const registered = await request.post(`${base}/auth/register`, {
    data: { username, email: `${username}@example.com`, password },
  });
  expect(registered.ok()).toBe(true);
  const login = await request.post(`${base}/auth/login`, {
    data: { username_or_email: username, password },
  });
  expect(login.ok()).toBe(true);
  const { access_token: token } = await login.json();
  const headers = { Authorization: `Bearer ${token}` };
  const profile = await request.put(`${base}/users/me`, {
    headers, data: { culinary_preferences: ["Italian"] },
  });
  expect(profile.ok()).toBe(true);
  for (const cuisine of ["Italian", "Mexican"]) {
    const created = await request.post(`${base}/recipes`, { headers, data: {
      title: `${username} ${cuisine}`, cuisine, difficulty: "easy",
      ingredients: [{ name: "Rice", amount: 1, unit: "cup" }],
      steps: [{ step_number: 1, instruction: "Cook the rice" }],
    } });
    expect(created.ok()).toBe(true);
  }
  await page.goto("/");
  await page.evaluate((value) => localStorage.setItem("simmer_token", value), token);
  await page.reload();
  const section = page.getByRole("region", { name: "Recommended for You" });
  await expect(section.getByRole("link", { name: new RegExp(`${username} Italian`) }))
    .toBeVisible();
  await expect(section.getByText(`${username} Mexican`)).toHaveCount(0);
  await page.getByRole("button", { name: "Log out" }).click();
  await expect(section).toHaveCount(0);
  await expect(page.getByRole("heading", { name: "Trending Recipes This Week" })).toBeVisible();
});
