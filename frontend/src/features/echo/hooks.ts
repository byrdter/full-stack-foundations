import { useMutation } from "@tanstack/react-query";

import { sendEcho } from "./api";
import type { EchoRequest, EchoResponse } from "./types";

export function useEcho() {
  return useMutation<EchoResponse, Error, EchoRequest>({
    mutationKey: ["echo"],
    mutationFn: sendEcho,
  });
}
