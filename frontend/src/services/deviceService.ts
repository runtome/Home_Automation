import apiClient from "@/services/apiClient";
import { Device, PaginatedResponse } from "@/types/device";

export const deviceService = {
  async list(): Promise<Device[]> {
    const { data } = await apiClient.get<PaginatedResponse<Device>>("/devices", {
      params: { page: 1, page_size: 200 },
    });
    return data.items;
  },

  async turnOn(id: number): Promise<Device> {
    const { data } = await apiClient.post<Device>(`/devices/${id}/on`);
    return data;
  },

  async turnOff(id: number): Promise<Device> {
    const { data } = await apiClient.post<Device>(`/devices/${id}/off`);
    return data;
  },

  async toggle(id: number): Promise<Device> {
    const { data } = await apiClient.post<Device>(`/devices/${id}/toggle`);
    return data;
  },
};
