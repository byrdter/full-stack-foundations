import { createContext, useCallback, useContext, useMemo, useState } from "react";
import type { PropsWithChildren } from "react";

type ToastVariant = "info" | "error" | "success";

type ToastItem = {
  id: number;
  message: string;
  variant: ToastVariant;
};

type ToastContextValue = {
  toasts: ToastItem[];
  pushToast: (message: string, variant?: ToastVariant) => void;
  removeToast: (id: number) => void;
};

const ToastContext = createContext<ToastContextValue | null>(null);

export function ToastProvider({ children }: PropsWithChildren) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const pushToast = useCallback((message: string, variant: ToastVariant = "info") => {
    setToasts((prev) => [...prev, { id: Date.now(), message, variant }]);
  }, []);

  const removeToast = useCallback((id: number) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  const value = useMemo(() => ({ toasts, pushToast, removeToast }), [toasts, pushToast, removeToast]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return ctx;
}

type ToastContainerProps = {
  toasts: ToastItem[];
  onDismiss: (id: number) => void;
};

function ToastContainer({ toasts, onDismiss }: ToastContainerProps) {
  if (!toasts.length) return null;

  return (
    <div
      aria-live="polite"
      role="status"
      style={{
        position: "fixed",
        top: "1rem",
        right: "1rem",
        display: "flex",
        flexDirection: "column",
        gap: "0.5rem",
        maxWidth: "320px",
        zIndex: 10,
      }}
    >
      {toasts.map((toast) => (
        <div
          key={toast.id}
          style={{
            padding: "0.75rem 1rem",
            borderRadius: "8px",
            boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
            background: backgroundForVariant(toast.variant),
            color: "#0f172a",
            display: "flex",
            justifyContent: "space-between",
            gap: "0.75rem",
          }}
        >
          <span>{toast.message}</span>
          <button
            aria-label="Dismiss notification"
            onClick={() => onDismiss(toast.id)}
            style={{
              border: "none",
              background: "transparent",
              cursor: "pointer",
              color: "#0f172a",
              fontWeight: 600,
            }}
          >
            ×
          </button>
        </div>
      ))}
    </div>
  );
}

function backgroundForVariant(variant: ToastVariant) {
  switch (variant) {
    case "success":
      return "#dcfce7";
    case "error":
      return "#fee2e2";
    case "info":
    default:
      return "#e0f2fe";
  }
}
