import { createApiClient } from "@/api/openapi-client";

import type { EchoRequest, EchoResponse } from "./types";

const client = createApiClient();

export async function sendEcho(payload: EchoRequest): Promise<EchoResponse> {
  return client.POST("/health/echo", payload) as Promise<EchoResponse>;
}
