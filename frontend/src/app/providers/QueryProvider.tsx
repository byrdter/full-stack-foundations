import { MutationCache, QueryCache, QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { PropsWithChildren } from "react";
import { useState } from "react";

import { useToast } from "@/shared/components/Toast";
import { normalizeError } from "@/shared/lib/httpError";

export function QueryProvider({ children }: PropsWithChildren) {
  const { pushToast } = useToast();

  const [queryClient] = useState(
    () =>
      new QueryClient({
        queryCache: new QueryCache({
          onError: (error) => {
            const normalized = normalizeError(error);
            pushToast(normalized.message, "error");
          },
        }),
        mutationCache: new MutationCache({
          onError: (error) => {
            const normalized = normalizeError(error);
            pushToast(normalized.message, "error");
          },
        }),
        defaultOptions: {
          queries: {
            refetchOnWindowFocus: false,
            retry: 1,
            staleTime: 30_000,
          },
        },
      }),
  );

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
