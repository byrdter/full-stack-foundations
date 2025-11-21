# AI-Optimized Codebase Foundations – Master Notes

These notes summarize key decisions, philosophy, and structure for the course we are designing, so future chats in this Project can stay aligned with what has already been done.

---

## 1. Project Overview

**Working title:**  
**AI-Optimized Codebase Foundations: Building Full-Stack Projects With an AI Coding Assistant**

**Goal:**  
Teach two primary learners (the author’s sons, late 30s, Master’s in IT, rusty on coding) – and potentially a wider audience – how to:

- Set up **AI-optimized full-stack codebases** (frontend + backend) with strong foundations.
- Use an **AI coding assistant** safely and effectively via **small, task-sized PIV loops**.
- Build confidence and reliability in AI-generated code through **guardrails**: tests, types, logging, structure.

**Learner profile:**

- Background in IT / systems / analysis.
- Some past programming experience but **out of practice**.
- New or relatively new to:
  - Python
  - React + TypeScript
  - AI coding workflows (PIV, prompting, etc.)
  - Modern tooling like uv, modern React build tools, Docker.

**Teaching format:**

- Short, focused lessons (Loom-style videos).
- Each lesson has:
  - A clear learning goal.
  - A small, concrete outcome.
  - A slide deck + rough script/teacher notes.
- Course is built around **demonstrations** plus explanations, not just theory.

---

## 2. Core Philosophy

### 2.1 AI as a Coding Assistant (Not a Magic Box)

- AI coding = using an AI assistant **inside real projects**, not just chatting for random snippets.
- We assume a **full-stack** environment:
  - `frontend/` → React + TypeScript
  - `backend/` → Python + FastAPI + Postgres
- LLM is treated as a **super-fast junior developer**:
  - Great at boilerplate, repetition, and pattern copying.
  - Weak at business rules, edge cases, UX subtleties.
  - Can be confidently wrong in both TS and Python.

### 2.2 Guardrails

To keep AI-generated changes reliable, we rely on **guardrails** on both frontend and backend.

**Backend guardrails:**

- Tests – `pytest`, clear test structure, good coverage.
- Linting & style – Ruff, Black.
- Type checking – MyPy or Pyright.
- Logging – structured logs around key operations.
- Architecture – vertical slice or similar structure for features/services.

**Frontend guardrails:**

- Unit & component tests – Jest/Vitest + React Testing Library.
- E2E tests – Cypress or Playwright for key flows.
- Linting/formatting – ESLint + Prettier.
- Types – TypeScript (prefer strict mode).
- Architecture – feature folders, shared components/hooks, error boundaries.

**Key idea:**  
We **build these foundations early**, *before* heavy feature development or complex agents.

---

## 3. PIV Loop & Task Philosophy

### 3.1 PIV = Plan → Implement → Validate

Core loop:

1. **Plan**  
   - Clarify the goal of a single, small task.  
   - Decide which layer/lane (frontend or backend).  
   - Choose tools, files, tests, and validations to use.

2. **Implement**  
   - Use the AI + human judgment to make the change.  
   - Keep the scope small and localized.

3. **Validate**  
   - Run tests, linters, and type checkers.  
   - Check logs and/or browser behavior.  
   - Confirm the task goal is met.

### 3.2 PIV Lanes: Frontend vs Backend

- Most PIV loops are **lane-specific**:
  - A **backend PIV** inside `backend/`  
  - A **frontend PIV** inside `frontend/`
- This keeps each task simpler:
  - One set of tools and checks per loop.
  - Low risk of confusion for the AI and the learner.

**Integration features** are built as **multiple small PIVs**, e.g.:

- PIV 1 (backend): Add a new API endpoint.
- PIV 2 (frontend): Call that endpoint and display data.
- PIV 3 (optional): Add an end-to-end test to verify the full flow.

### 3.3 Task Size

- Each PIV loop should handle **one clearly defined task**:
  - e.g., “Add a `/health` endpoint”, **or**
  - “Add a loading state & error message to this React component”.
- Small tasks → easier validation → fewer hallucinations → better learning.

---

## 4. Tech Stack Choices & Alternatives

### 4.1 Backend

**Primary stack for the course:**

- Language: **Python**
- Framework: **FastAPI**
- Database: **PostgreSQL**
- Tooling:
  - **uv** for Python environment & dependency management.
  - pytest for tests.
  - Ruff + Black for linting & formatting.
  - MyPy/Pyright for type checking.
  - Docker for backend + DB in dev/prod.

**Alternatives to mention (but not focus on):**

- Languages: Java, Go, Node/TypeScript.
- Frameworks:
  - Java: Spring Boot.
  - Go: Gin, Fiber.
  - Node: Express, NestJS.
- Databases: MySQL, SQLite, MongoDB.

### 4.2 Frontend

**Primary stack for the course:**

- Framework: **React**
- Language: **TypeScript**
- Build tooling: Vite or similar modern tool.
- Testing:
  - Jest or Vitest + React Testing Library.
  - Cypress or Playwright for E2E.

**Alternatives to mention:**

- Frameworks: Next.js, Angular, Vue, Svelte.
- Language: JavaScript (with note on why TypeScript is preferred here).

### 4.3 Infrastructure

- Docker primarily for:
  - Backend service(s)
  - Postgres DB
- Frontend:
  - In development: usually run via `npm run dev`/`pnpm dev` (not necessarily in Docker).
  - In production: can be containerized or served as static assets (out of scope for early tracks).

**Important architecture note:**  
The frontend **does not** directly talk to Postgres; it talks to the backend API, which talks to the DB.

---

## 5. Course Structure So Far

### 5.1 Big Picture

The course is broken into **tracks**, each with short lessons.  
Tracks already discussed (only Track 1 fully fleshed out so far):

- **Track 1 – Big Picture & PIV Mindset (Full-Stack)**
- (Future) Track – Backend Foundations (Python/FastAPI/Postgres)
- (Future) Track – Frontend Foundations (React/TypeScript)
- (Future) Track – Applying PIV with AI across the stack
- (Future) Track – Agents & higher-level AI workflows

Only Track 1 + Lesson 1 are concretely drafted so far.

---

### 5.2 Track 1 – Big Picture & PIV Mindset (Full-Stack)

**Purpose:**  
Give learners a conceptual foundation:

- What AI coding really is (full-stack context).
- How PIV works.
- What the modern stack looks like.
- Why AI-optimized foundations matter for both frontend and backend.

**Lessons in Track 1:**

#### Lesson 1 – What Is AI Coding? (Full-Stack)

- Reframes AI coding from “paste snippets” to “collaborate with an AI inside real projects”.
- Explicitly mentions:
  - `frontend/`: React + TS
  - `backend/`: Python + FastAPI + Postgres
- Introduces AI as a **super-fast junior dev** with strengths/weaknesses.
- Introduces guardrails on both frontend and backend.
- Explains why we’re starting with foundations first.
- Assets already created:
  - `lesson-01-what-is-ai-coding-fullstack.md` (script/notes)
  - `Lesson_1_What_is_AI_Coding_Fullstack_Terry_Byrd.pptx` (slides)

#### Lesson 2 – The PIV Loop: Plan → Implement → Validate

- Defines the PIV loop.
- Shows non-coding example (e.g., planning a trip).
- Shows a **backend-only PIV** example (e.g., `/health` endpoint).
- Shows a **frontend-only PIV** example (e.g., loading & error state in a React component).
- Explains “lanes”:
  - PIV loops are usually **frontend-only** or **backend-only**.
- Describes multi-PIV sequences for full-stack features:
  - Backend PIV → Frontend PIV → optional integration PIV.
- Includes a simple activity: learners outline a PIV loop for a small task of their own.

*(Lesson 2 detailed script/slide deck still to be created.)*

#### Lesson 3 – Modern Full-Stack: Frontend → Backend → Database → Infra

- Explains layers of a modern app:
  - Frontend (React/TS)
  - Backend (Python/FastAPI)
  - Database (Postgres)
  - Infrastructure (Docker, hosting)
- Shows similar “shapes” using alternative stacks (e.g., Angular + Java).
- Clarifies:
  - Frontend runs in the browser, talks to backend via HTTP.
  - Backend enforces rules and talks to the DB.
  - DB stores data; only backend talks to it.
  - Docker is mainly used for backend + DB in this course.
- Sets up learners to understand where each tool and track fits.

*(Lesson 3 detailed script/slide deck still to be created.)*

#### Lesson 4 – What Is an AI-Optimized Codebase, and Why Build It First?

- Defines “AI-optimized foundation” for:
  - Backend: tests, logging, infra, DB layer, monitoring, shared patterns.
  - Frontend: tests, linting, TS, error handling, feature structure.
- Explains how each pillar helps AI coding:
  - Tests catch AI mistakes.
  - Types guide and constrain the AI.
  - Logging and structure make debugging easier.
- Introduces the idea of reusable **template repos**:
  - Backend template.
  - Frontend template.
- Summarizes Track 1 and tees up next tracks (Backend Foundations, Frontend Foundations).

*(Lesson 4 detailed script/slide deck still to be created.)*

---

## 6. Key Source Materials (Uploaded Files)

The following files from the original workshop/course are assumed to be uploaded into this Project:

1. **`BuildingAICodebases.md`**
   - Transcript of the “Building AI Codebases” workshop.
   - Describes the AI-optimized codebase process used by the original presenter.

2. **`ai-coding-project-setup-guide.md`**
   - Step-by-step guide for AI coding project setup (backend-focused).
   - Includes environment setup, tooling, etc.

3. **`vertical-slice-architecture-setup-guide.md`**
   - Describes vertical slice architecture for the backend.
   - Important for designing backend structure in an AI-friendly way.

4. **`create-prompt.md`**
   - The standard prompt used for AI coding in the workshop.
   - Likely includes structured instructions for PIV-like interactions with the LLM.

5. **`README.md` (course README from the original repo)**
   - Provides high-level context of the original course and examples.
   - Not strictly needed for Track 1 but helpful for alignment.

6. **GitHub template:**  
   - `https://github.com/byrdter/fastapi-starter-for-ai-coding`
   - Backend template produced during the workshop (for future tracks).

---

## 7. Files Already Created in This Course Design

These should be uploaded into the Project as well:

1. **Track 1 curriculum (full-stack aware):**
   - `track-1-big-picture-and-piv-fullstack.md`

2. **Lesson 1 script:**
   - `lesson-01-what-is-ai-coding-fullstack.md`

3. **Lesson 1 slide deck:**
   - `Lesson_1_What_is_AI_Coding_Fullstack_Terry_Byrd.pptx`

*(More lesson scripts and slide decks will be created later.)*

---

## 8. Style & Teaching Constraints

- Lessons should be **short and focused**, suitable for:
  - Loom-style video recording.
  - Public consumption (but aimed primarily at the author’s sons).
- Emphasis on:
  - Clear explanations using **simple language**.
  - Connecting new concepts to learners’ prior IT/enterprise experience.
  - Demonstrating **small, realistic tasks** rather than huge demos.
- Course should be:
  - **Stack-aware but not dogmatic** – mention alternatives, but focus on Python/FastAPI and React/TS.
  - **Strongly grounded in PIV** – every step is Plan → Implement → Validate.
  - **Foundations-first** – build the AI-optimized frontend and backend templates before heavy agent work.

---

## 9. Next Planned Work (for Future Chats)

When continuing in this Project, likely next steps are:

1. Flesh out **Lesson 2 – PIV Loop** script + slides (full-stack, with lanes).
2. Flesh out **Lesson 3 – Modern Full-Stack** script + slides.
3. Flesh out **Lesson 4 – AI-Optimized Codebase** script + slides.
4. Design:
   - Backend Foundations track (Python/FastAPI/Postgres).
   - Frontend Foundations track (React/TypeScript).
5. Later:
   - Show how to use the AI coding prompt (from `create-prompt.md`) in real PIV loops.
   - Design small, lane-specific tasks with AI-driven implementation and solid validation.

---