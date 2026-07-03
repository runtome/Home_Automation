export type Role = "admin" | "user";

export interface User {
  id: number;
  username: string;
  email: string;
  role: Role;
  created_at: string;
}
