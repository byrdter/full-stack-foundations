import { useQuery } from "@tanstack/react-query";

import { fetchReadiness } from "./api";
import type { ReadinessStatus } from "./types";

export function useReadinessStatus() {
  return useQuery<ReadinessStatus, Error>({
    queryKey: ["readiness"],
    queryFn: fetchReadiness,
    retry: 0,
  });
}
