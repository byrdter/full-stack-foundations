import { rest } from "msw";

const apiBase = "http://localhost:8123/api";

// Extend this list with real endpoints as features are added.
export const handlers = [
  rest.get(`${apiBase}/health`, (_req, res, ctx) => {
    return res(ctx.status(200), ctx.json({ status: "ok" }));
  }),
  rest.get(`${apiBase}/health/ready`, (_req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({ status: "ready", environment: "development", database: "connected" }),
    );
  }),
  rest.post(`${apiBase}/health/echo`, async (req, res, ctx) => {
    const body = await req.json();
    return res(ctx.status(200), ctx.json({ message: (body as { message: string }).message }));
  }),
];
