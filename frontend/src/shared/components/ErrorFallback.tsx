type ErrorFallbackProps = {
  title?: string;
  message?: string;
  onRetry?: () => void;
};

export function ErrorFallback({
  title = "Something went wrong.",
  message = "Try again or refresh the page.",
  onRetry,
}: ErrorFallbackProps) {
  return (
    <div
      role="alert"
      style={{
        border: "1px solid #e11d48",
        background: "#fef2f2",
        color: "#991b1b",
        padding: "1rem",
        borderRadius: "8px",
        margin: "1rem 0",
      }}
    >
      <h2 style={{ margin: "0 0 0.5rem 0" }}>{title}</h2>
      <p style={{ margin: "0 0 1rem 0" }}>{message}</p>
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          style={{
            padding: "0.5rem 0.75rem",
            borderRadius: "6px",
            border: "1px solid #e11d48",
            background: "#be123c",
            color: "#fff",
            cursor: "pointer",
          }}
        >
          Retry
        </button>
      ) : null}
    </div>
  );
}
