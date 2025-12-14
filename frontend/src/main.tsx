import React from "react";
import ReactDOM from "react-dom/client";

import App from "@/app/App";
import { QueryProvider } from "@/app/providers/QueryProvider";
import { ErrorBoundary } from "@/shared/components/ErrorBoundary";
import { ErrorFallback } from "@/shared/components/ErrorFallback";
import { ToastProvider } from "@/shared/components/Toast";

const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("Root element not found");
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <ErrorBoundary fallback={<ErrorFallback onRetry={() => window.location.reload()} />}>
      <ToastProvider>
        <QueryProvider>
          <App />
        </QueryProvider>
      </ToastProvider>
    </ErrorBoundary>
  </React.StrictMode>,
);
