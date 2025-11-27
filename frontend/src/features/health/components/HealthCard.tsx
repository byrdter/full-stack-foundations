import { useHealthStatus } from "../hooks";

export function HealthCard() {
  const { data, isLoading, isError } = useHealthStatus();

  if (isLoading) {
    return (
      <section aria-busy="true">
        <p>Checking health...</p>
      </section>
    );
  }

  if (isError) {
    return (
      <section role="status" aria-live="polite">
        <p>Service is unavailable.</p>
      </section>
    );
  }

  return (
    <section role="status" aria-live="polite">
      <p>Service status: {data?.status ?? "unknown"}</p>
    </section>
  );
}
