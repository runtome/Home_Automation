export type DeviceStatus = "ON" | "OFF" | "UNKNOWN";

export interface Device {
  id: number;
  device_id: string;
  device_name: string;
  room: string;
  status: DeviceStatus;
  online: boolean;
  ip_address: string | null;
  mac_address: string | null;
  firmware: string | null;
  rssi: number | null;
  last_seen: string | null;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface DeviceUpdateMessage {
  type: "device_update";
  data: Device;
}
