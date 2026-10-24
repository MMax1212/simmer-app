import { test, expect } from "@playwright/test";

// --- US1.1, US1.3, US1.4, US1.5: Complete Sprint 1 End-to-End User Journey in Real Browser ---
test("register, edit profile, create/edit recipe, reload library, and delete", async ({ page }) => {
  const username = "cook_" + Date.now();
  // --- US1.1: User Account Registration ---
  await page.goto("/register");
  await page.getByLabel("Email", { exact: true }).fill(username + "@example.com");
  await page.getByLabel("Username", { exact: true }).fill(username);
  await page.getByLabel("Password", { exact: true }).fill("😀".repeat(20));
  await page.getByLabel("Confirm password").fill("😀".repeat(20));
  await page.getByRole("button", { name: "Sign up" }).click();
  await expect(page).toHaveURL(/\/profile$/);

  // --- US1.3: User Profile Configuration (Bio & Culinary Tags) ---
  await page.getByLabel("Bio").fill("Learning to cook");
  await page.getByLabel("Italian", { exact: true }).check();
  await page.getByRole("button", { name: "Save profile" }).click();
  await expect(page.getByText("Profile saved.")).toBeVisible();
  await page.reload();
  await expect(page.getByLabel("Bio")).toHaveValue("Learning to cook");
  await expect(page.getByLabel("Italian", { exact: true })).toBeChecked();

  // --- US1.5: Personal Recipe Tab (Initial Empty State) ---
  await page.getByRole("link", { name: "My Recipes", exact: true }).click();
  await expect(page.getByText("No recipes yet.", { exact: false })).toBeVisible();

  // --- US1.4: Recipe Authoring (Form Fields, Ingredients & Multi-Step Instructions) ---
  await page.getByRole("link", { name: "New Recipe", exact: true }).click();
  await page.getByLabel("Title", { exact: true }).fill("Browser Pasta");
  await page.getByLabel("Cuisine").fill("Italian");
  await page.getByLabel("Meal type").fill("Dinner");
  await page.getByLabel("Difficulty").selectOption("easy");
  await page.getByLabel("Amount 1").fill("200");
  await page.getByLabel("Unit 1").fill("g");
  await page.getByLabel("Ingredient 1", { exact: true }).fill("pasta");
  await page.getByLabel("Step 1", { exact: true }).fill("Boil the pasta");
  await page.getByRole("button", { name: "+ Add step" }).click();
  await page.getByLabel("Step 2", { exact: true }).fill("Add tomato sauce");
  await page.getByRole("button", { name: "Save recipe" }).click();

  // --- US1.5: Recipe Detail View ---
  await expect(page.getByRole("heading", { name: "Browser Pasta" })).toBeVisible();
  await expect(page.getByText("Add tomato sauce", { exact: true })).toBeVisible();
  await expect(page.locator("article ol")).toHaveCSS("list-style-type", "decimal");
  await page.screenshot({ path: test.info().outputPath("recipe-detail.png"), fullPage: true });

  // --- US1.4: Recipe Editing ---
  await page.getByRole("link", { name: "Edit", exact: true }).click();
  await page.getByLabel("Title", { exact: true }).fill("Better Browser Pasta");
  await page.getByRole("button", { name: "Remove step 1" }).click();
  await page.getByRole("button", { name: "Save recipe" }).click();
  await expect(page.getByRole("heading", { name: "Better Browser Pasta" })).toBeVisible();

  // --- US1.5: Personal Recipe Library Dashboard & Deletion ---
  await page.getByRole("link", { name: "My Recipes", exact: true }).click();
  await page.reload();
  await page.getByRole("heading", { name: "Better Browser Pasta" }).click();
  page.once("dialog", (dialog) => dialog.accept());
  await page.getByRole("button", { name: "Delete", exact: true }).click();
  await expect(page.getByText("No recipes yet.", { exact: false })).toBeVisible();

  // --- US1.1: Logout and Login with Username ---
  await page.getByRole("button", { name: "Log out" }).click();
  await page.getByRole("link", { name: "Log in", exact: true }).first().click();
  await page.getByLabel("Username or email").fill(username);
  await page.getByLabel("Password", { exact: true }).fill("😀".repeat(20));
  await page.getByRole("button", { name: "Log in", exact: true }).click();
  await expect(page).toHaveURL(/\/recipes\/my-recipes$/);
});

// --- US1.1: Security & Session Handling (Invalid/Expired Token Redirect) ---
test("an invalid saved token redirects to login and is removed", async ({ page }) => {
  await page.goto("/");
  await page.evaluate(() => localStorage.setItem("simmer_token", "expired-or-invalid-token"));
  await page.goto("/profile");
  await expect(page).toHaveURL(/\/login$/);
  expect(await page.evaluate(() => localStorage.getItem("simmer_token"))).toBeNull();
});
