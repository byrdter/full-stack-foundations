import { ApiError } from "@/api/client";

export type NormalizedError = {
  message: string;
  status?: number;
};

export function normalizeError(error: unknown): NormalizedError {
  if (error instanceof ApiError) {
    return {
      message: error.details && typeof error.details === "object" && "detail" in (error.details as Record<string, unknown>)
        ? String((error.details as { detail?: unknown }).detail ?? "Request failed")
        : error.message,
      status: error.status,
    };
  }

  if (error instanceof Error) {
    return { message: error.message };
  }

  return { message: "Something went wrong" };
}
