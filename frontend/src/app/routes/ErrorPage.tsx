import { isRouteErrorResponse, useRouteError } from "react-router-dom";

import { ErrorFallback } from "@/shared/components/ErrorFallback";

export function ErrorPage() {
  const error = useRouteError();

  if (isRouteErrorResponse(error)) {
    return (
      <ErrorFallback
        title={`Error ${error.status}`}
        message={error.statusText || "An unexpected error occurred."}
        onRetry={() => window.location.assign("/")}
      />
    );
  }

  return <ErrorFallback onRetry={() => window.location.assign("/")} />;
}
