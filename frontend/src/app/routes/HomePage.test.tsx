import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { rest } from "msw";
import { createMemoryRouter, RouterProvider } from "react-router-dom";

import { server } from "../../../tests/test-server";
import { router as appRouter } from "../router";

function renderWithRouter() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  const router = createMemoryRouter(appRouter.routes, { initialEntries: ["/"] });

  render(
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>,
  );
}

describe("HomePage route", () => {
  it("shows health status after fetch", async () => {
    server.use(
      rest.get("http://localhost:8123/api/health", (_req, res, ctx) => {
        return res(ctx.json({ status: "ok" }));
      }),
    );

    renderWithRouter();

    expect(screen.getByText(/health check/i)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText(/service status: ok/i)).toBeInTheDocument();
    });
  });
});
