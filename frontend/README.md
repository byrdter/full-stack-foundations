# Frontend (React + TypeScript + Vite)

Backend service lives in `../backend`; start it there when you need real API responses or to generate OpenAPI types.

## Setup
1. Copy `.env.example` to `.env` and adjust `VITE_API_BASE_URL` if needed.
2. Install dependencies (choose one):
   - `npm install`
   - `pnpm install`
   - `yarn install`

## Commands
- `npm run dev` – start Vite dev server (default port 5173)
- `npm run build` – production build
- `npm run preview` – preview the built app
- `npm run lint` – ESLint
- `npm run typecheck` – TypeScript strict check
- `npm run format` / `npm run format:fix` – Prettier checks/fixes
- `npm run test` – Vitest (headless)
- `npm run test:watch` – Vitest watch mode
- `npm run test:cov` – Vitest coverage
- `npm run test:e2e` – Playwright smoke tests (mocks health endpoint)
- `npm run test:e2e:ui` – Playwright UI mode
- `npm run openapi` – generate `src/api/schemas.ts` from running backend `/openapi.json`

## Notes
- Path alias `@/` points to `src/`.
- Guardrails scaffolded: ESLint, Prettier, Vitest + React Testing Library + MSW, React Query for data, Playwright for E2E.
- Husky + lint-staged are configured; after installing deps run `npm run prepare` once to activate hooks (pre-commit runs lint-staged).
- Playwright needs browsers installed once: `npx playwright install`.
- OpenAPI types: run backend, then `npm run openapi` to overwrite `src/api/schemas.ts`.
- Query/mutation errors surface to toasts via the QueryProvider’s global handlers.
- OpenAPI: run backend then `npm run openapi` to generate `src/api/schemas.ts`; `createApiClient` wraps the generated `paths` types.
- Example slices: health (GET), readiness (GET), echo (POST) with MSW + Vitest + Playwright coverage.
