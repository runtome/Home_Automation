import apiClient from "@/services/apiClient";
import { Log } from "@/types/log";
import { PaginatedResponse } from "@/types/device";

export const logService = {
  async recent(pageSize = 10): Promise<Log[]> {
    const { data } = await apiClient.get<PaginatedResponse<Log>>("/logs", {
      params: { page: 1, page_size: pageSize },
    });
    return data.items;
  },
};
