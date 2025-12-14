import { test, expect } from "@playwright/test";

test.describe("Echo form (toasts)", () => {
  test.beforeEach(async ({ page, baseURL }) => {
    await page.route("**/health", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ status: "ok" }),
      });
    });

    await page.route("**/health/ready", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ status: "ready", environment: "development", database: "connected" }),
      });
    });

    await page.route("**/health/echo", async (route) => {
      const reqBody = await route.request().postDataJSON();
      if (reqBody?.message === "fail") {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({ detail: "boom" }),
        });
        return;
      }
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ message: reqBody?.message ?? "ok" }),
      });
    });

    await page.goto(baseURL ?? "http://localhost:5173");
  });

  test("shows toast on mutation error", async ({ page }) => {
    await page.getByLabel(/echo message/i).fill("fail");
    await page.getByRole("button", { name: /send/i }).click();

    await expect(page.getByText(/something went wrong/i)).toBeVisible();
  });
});
