export interface Log {
  id: number;
  user_id: number | null;
  device_id: number | null;
  action: string;
  message: string | null;
  created_at: string;
}
