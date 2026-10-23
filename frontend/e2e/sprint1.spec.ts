import { test, expect } from "@playwright/test";
test("register, reload, log out and log in using a username", async ({ page }) => {
    const username = "account_" + Date.now();
    await page.goto("/register");
    await page.getByLabel("Email", { exact: true }).fill(username + "@example.com");
    await page.getByLabel("Username", { exact: true }).fill(username);
    await page.getByLabel("Password", { exact: true }).fill("😀".repeat(20));
    await page.getByLabel("Confirm password").fill("😀".repeat(20));
    await page.getByRole("button", { name: "Sign up" }).click();
    await expect(page.getByRole("heading", { name: "Welcome back, " + username })).toBeVisible();
    await page.reload();
    await expect(page.getByRole("heading", { name: "Welcome back, " + username })).toBeVisible();
    await page.getByRole("button", { name: "Log out" }).click();
    await page.getByRole("link", { name: "Log in", exact: true }).first().click();
    await page.getByLabel("Username or email").fill(username);
    await page.getByLabel("Password", { exact: true }).fill("😀".repeat(20));
    await page.getByRole("button", { name: "Log in", exact: true }).click();
    await expect(page.getByRole("heading", { name: "Welcome back, " + username })).toBeVisible();
});
test("an invalid saved token is removed before entering admin", async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.setItem("simmer_token", "invalid-token"));
    await page.goto("/admin");
    await expect(page.getByRole("heading", { name: "Log in" })).toBeVisible();
    expect(await page.evaluate(() => localStorage.getItem("simmer_token"))).toBeNull();
});
