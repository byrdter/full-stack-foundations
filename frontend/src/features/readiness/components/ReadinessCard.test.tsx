import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { rest } from "msw";

import { server } from "@tests/test-server";

import { ReadinessCard } from "./ReadinessCard";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

describe("ReadinessCard", () => {
  it("renders readiness details", async () => {
    server.use(
      rest.get("http://localhost:8123/api/health/ready", (_req, res, ctx) => {
        return res(ctx.json({ status: "ready", environment: "development", database: "connected" }));
      }),
    );

    render(
      <QueryClientProvider client={queryClient}>
        <ReadinessCard />
      </QueryClientProvider>,
    );

    expect(screen.getByText(/verifying readiness/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(/service status: ready/i)).toBeInTheDocument();
      expect(screen.getByText(/environment: development/i)).toBeInTheDocument();
      expect(screen.getByText(/database: connected/i)).toBeInTheDocument();
    });
  });
});
