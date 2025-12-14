import { EchoForm } from "@/features/echo/components/EchoForm";
import { HealthCard } from "@/features/health/components/HealthCard";
import { ReadinessCard } from "@/features/readiness/components/ReadinessCard";

export function HomePage() {
  return (
    <div>
      <header style={{ marginBottom: "1rem" }}>
        <h1>Frontend foundation ready</h1>
        <p>
          Vite + React + TypeScript scaffold with strict settings and path aliases. Guardrails,
          routing, and data fetching are wired.
        </p>
      </header>

      <section aria-labelledby="health">
        <h2 id="health">Health check</h2>
        <HealthCard />
      </section>

      <section aria-labelledby="readiness" style={{ marginTop: "1rem" }}>
        <h2 id="readiness">Readiness</h2>
        <ReadinessCard />
      </section>

      <section aria-labelledby="echo" style={{ marginTop: "1rem" }}>
        <h2 id="echo">Echo (POST example)</h2>
        <p style={{ marginBottom: "0.5rem" }}>
          Sends a message to the backend and shows success/error via toasts and inline state.
        </p>
        <EchoForm />
      </section>
    </div>
  );
}
