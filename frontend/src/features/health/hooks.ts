import { useQuery } from "@tanstack/react-query";

import { fetchHealth } from "./api";
import type { HealthStatus } from "./types";

export function useHealthStatus() {
  return useQuery<HealthStatus, Error>({
    queryKey: ["health"],
    queryFn: fetchHealth,
    retry: 0,
    select: (data) => data,
    meta: { feature: "health" },
    throwOnError: false,
  });
}
