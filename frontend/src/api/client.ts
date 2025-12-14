export type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

export interface RequestConfig {
  path: string;
  method?: HttpMethod;
  body?: unknown;
  headers?: Record<string, string>;
}

const API_BASE_URL = (import.meta.env?.VITE_API_BASE_URL as string | undefined) ?? "http://localhost:8123/api";

export class ApiError extends Error {
  status: number;
  details?: unknown;

  constructor(message: string, status: number, details?: unknown) {
    super(message);
    this.status = status;
    this.details = details;
  }
}

export async function apiRequest<T>({ path, method = "GET", body, headers = {} }: RequestConfig): Promise<T> {
  if (!API_BASE_URL) {
    throw new Error("VITE_API_BASE_URL is not set.");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  const contentType = response.headers.get("content-type") ?? "";
  const isJson = contentType.includes("application/json");
  const data = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    const errorMessage = isJson && data?.detail ? String(data.detail) : "Request failed";
    throw new ApiError(errorMessage, response.status, data);
  }

  return data as T;
}
