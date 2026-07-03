import { useQuery } from "@tanstack/react-query";

import { logService } from "@/services/logService";

export const LOGS_KEY = ["logs"];

export function useLogs(pageSize = 10) {
  return useQuery({
    queryKey: LOGS_KEY,
    queryFn: () => logService.recent(pageSize),
    refetchInterval: 30_000,
  });
}
