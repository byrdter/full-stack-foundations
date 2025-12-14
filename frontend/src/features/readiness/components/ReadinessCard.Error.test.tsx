import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { rest } from "msw";

import { server } from "@tests/test-server";

import { ReadinessCard } from "./ReadinessCard";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

describe("ReadinessCard error state", () => {
  it("shows error message when readiness fails", async () => {
    server.use(
      rest.get("http://localhost:8123/api/health/ready", (_req, res, ctx) => {
        return res(ctx.status(503), ctx.json({ detail: "Application is not ready" }));
      }),
    );

    render(
      <QueryClientProvider client={queryClient}>
        <ReadinessCard />
      </QueryClientProvider>,
    );

    await waitFor(() => {
      expect(screen.getByText(/readiness check failed/i)).toBeInTheDocument();
      expect(screen.getByText(/application is not ready/i)).toBeInTheDocument();
    });
  });
});
