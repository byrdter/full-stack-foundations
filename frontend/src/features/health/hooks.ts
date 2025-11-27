import { useQuery } from "@tanstack/react-query";

import { fetchHealth } from "./api";
import type { HealthStatus } from "./types";
import { normalizeError } from "@/shared/lib/httpError";

export function useHealthStatus() {
  return useQuery<HealthStatus, Error>({
    queryKey: ["health"],
    queryFn: fetchHealth,
    retry: 0,
    select: (data) => data,
    meta: { feature: "health" },
    throwOnError: false,
    onError: (error) => {
      const normalized = normalizeError(error);
      console.warn("health.check_failed", normalized);
    },
  });
}
