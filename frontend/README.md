# Frontend (React + TypeScript + Vite)

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
- `npm run lint` – ESLint (add rules in upcoming guardrail step)
- `npm run typecheck` – TypeScript strict check

## Notes
- Path alias `@/` points to `src/` (Vite + TS configured).
- Guardrails (ESLint/Prettier/test tooling) will be added in the next step.
