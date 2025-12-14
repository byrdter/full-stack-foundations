import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { rest } from "msw";

import { server } from "@tests/test-server";

import { EchoForm } from "./EchoForm";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
});

describe("EchoForm", () => {
  it("submits and shows response text", async () => {
    server.use(
      rest.post("http://localhost:8123/api/health/echo", async (req, res, ctx) => {
        const body = await req.json();
        return res(ctx.json({ message: (body as { message: string }).message }));
      }),
    );

    render(
      <QueryClientProvider client={queryClient}>
        <EchoForm />
      </QueryClientProvider>,
    );

    fireEvent.change(screen.getByLabelText(/echo message/i), { target: { value: "hello" } });
    fireEvent.click(screen.getByRole("button", { name: /send/i }));

    await waitFor(() => {
      expect(screen.getByText(/response: hello/i)).toBeInTheDocument();
    });
  });

  it("shows error state on failure", async () => {
    server.use(
      rest.post("http://localhost:8123/api/health/echo", (_req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ detail: "boom" }));
      }),
    );

    render(
      <QueryClientProvider client={queryClient}>
        <EchoForm />
      </QueryClientProvider>,
    );

    fireEvent.change(screen.getByLabelText(/echo message/i), { target: { value: "hello" } });
    fireEvent.click(screen.getByRole("button", { name: /send/i }));

    await waitFor(() => {
      expect(screen.getByText(/failed to send/i)).toBeInTheDocument();
    });
  });
});
