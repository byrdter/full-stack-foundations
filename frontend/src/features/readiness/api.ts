import { createApiClient } from "@/api/openapi-client";

import type { ReadinessStatus } from "./types";

const client = createApiClient();

export async function fetchReadiness(): Promise<ReadinessStatus> {
  // Using path literal keeps consistency for future OpenAPI types.
  return client.GET("/health/ready") as Promise<ReadinessStatus>;
}
