import { useReadinessStatus } from "../hooks";

export function ReadinessCard() {
  const { data, isLoading, isError, error } = useReadinessStatus();

  if (isLoading) {
    return (
      <section aria-busy="true">
        <p>Verifying readiness...</p>
      </section>
    );
  }

  if (isError) {
    return (
      <section role="status" aria-live="polite">
        <p>Readiness check failed.</p>
        {error?.message ? <p style={{ fontSize: "0.9rem" }}>{error.message}</p> : null}
      </section>
    );
  }

  return (
    <section role="status" aria-live="polite">
      <p>Service status: {data?.status ?? "unknown"}</p>
      <p>Environment: {data?.environment ?? "unknown"}</p>
      <p>Database: {data?.database ?? "unknown"}</p>
    </section>
  );
}
