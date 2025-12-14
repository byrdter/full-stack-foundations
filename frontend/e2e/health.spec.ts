import { test, expect } from "@playwright/test";

test.beforeEach(async ({ page, baseURL }) => {
  // Mock health endpoints so the smoke test does not require the backend.
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
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ message: reqBody?.message ?? "ok" }),
    });
  });

  await page.goto(baseURL ?? "http://localhost:5173");
});

test("home page shows health status", async ({ page }) => {
  await expect(page.getByRole("heading", { name: /frontend foundation ready/i })).toBeVisible();
  await expect(page.getByText(/health check/i)).toBeVisible();
  await expect(page.getByText(/service status: ok/i)).toBeVisible();
  await expect(page.getByText(/readiness/i)).toBeVisible();
  await expect(page.getByText(/database: connected/i)).toBeVisible();

  await page.getByLabel(/echo message/i).fill("hi there");
  await page.getByRole("button", { name: /send/i }).click();
  await expect(page.getByText(/response: hi there/i)).toBeVisible();
});
