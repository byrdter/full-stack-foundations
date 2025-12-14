import { apiRequest } from "@/api/client";

import type { HealthStatus } from "./types";

export async function fetchHealth(): Promise<HealthStatus> {
  return apiRequest<HealthStatus>({ path: "/health" });
}
