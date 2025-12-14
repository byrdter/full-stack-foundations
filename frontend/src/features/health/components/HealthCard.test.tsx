import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { rest } from "msw";

import { server } from "@tests/test-server";

import { HealthCard } from "./HealthCard";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

describe("HealthCard", () => {
  it("renders loading, then health status", async () => {
    server.use(
      rest.get("http://localhost:8123/api/health", (_req, res, ctx) => {
        return res(ctx.json({ status: "ok" }));
      }),
    );

    render(
      <QueryClientProvider client={queryClient}>
        <HealthCard />
      </QueryClientProvider>,
    );

    expect(screen.getByText(/checking health/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(/service status: ok/i)).toBeInTheDocument();
    });
  });
});
