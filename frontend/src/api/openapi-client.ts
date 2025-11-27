import type { paths } from "./schemas";
import { apiRequest } from "./client";

type HttpMethod = keyof paths[keyof paths] & ("get" | "post" | "put" | "patch" | "delete");

type SuccessResponse<T> = T extends { responses: infer R }
  ? R extends { 200?: infer Ok }
    ? Ok extends { content: { "application/json": infer Body } }
      ? Body
      : unknown
    : unknown
  : unknown;

type RequestBody<T> = T extends { requestBody?: { content?: { "application/json"?: infer B } } }
  ? B
  : undefined;

type QueryParams<T> = T extends { parameters?: { query?: infer Q } } ? Q : undefined;

export interface ClientConfig {
  baseUrl?: string;
}

/**
 * Minimal OpenAPI-aware client using the generated `paths` type from openapi-typescript.
 * This is intentionally thin; it delegates to `apiRequest` for transport and logging.
 *
 * Example usage after running `npm run openapi`:
 *   const client = createApiClient();
 *   const health = await client.GET("/health");
 */
export function createApiClient(_config?: ClientConfig) {
  return {
    async GET<Path extends keyof paths>(path: Path, params?: QueryParams<paths[Path]["get"]>) {
      return apiRequest<SuccessResponse<paths[Path]["get"]>>({
        path: String(path),
        method: "GET",
        // Query params can be appended if provided; kept simple here.
        ...(params ? { path: appendQuery(path, params) } : {}),
      });
    },

    async POST<Path extends keyof paths>(
      path: Path,
      body?: RequestBody<paths[Path]["post"]>,
      params?: QueryParams<paths[Path]["post"]>,
    ) {
      return apiRequest<SuccessResponse<paths[Path]["post"]>>({
        path: String(params ? appendQuery(path, params) : path),
        method: "POST",
        body,
      });
    },
  };
}

function appendQuery(path: string | number | symbol, params: Record<string, unknown>) {
  const url = new URL(String(path), "http://localhost"); // base is ignored when returned
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null) return;
    url.searchParams.set(key, String(value));
  });
  return url.pathname + (url.search ? url.search : "");
}
