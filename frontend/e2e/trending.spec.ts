// Browser coverage complements component tests: JSDOM cannot detect page overflow,
// perform real scrolling, or prove that a rendered router link navigates on click.
import { test, expect } from "@playwright/test";

test("mobile trending cards scroll and open recipe details", async ({ page }) => {
  // Isolate card presentation from ranking; backend gravity is tested independently.
  await page.route("**/api/v1/recipes/trending?*", (route) => route.fulfill({ json:
    Array.from({ length: 5 }, (_, index) => ({
      id: index + 1, title: `Trending recipe ${index + 1}`, image_url: null,
      cuisine: "Italian", difficulty: "easy", cook_time_mins: 20,
      author_username: "ana", trending_score: 5 - index,
      likes_count: 2, completed_count: 1,
    })),
  }));
  // A narrow phone viewport exposes flex-width regressions hidden by desktop layouts.
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  const list = page.getByRole("list", { name: "Trending recipes" });
  await expect(list.getByRole("link")).toHaveCount(5);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.getByRole("button", { name: "Next trending recipes" }).click();
  // Poll the observable scroll position instead of relying on a timing-sensitive sleep.
  await expect.poll(() => list.evaluate((element) => element.scrollLeft)).toBeGreaterThan(0);
  await page.getByRole("button", { name: "Previous trending recipes" }).click();
  await list.getByRole("link").first().click();
  // This proves navigation only; recipe-detail content is covered by its own tests.
  await expect(page).toHaveURL(/\/recipes\/1$/);
});
