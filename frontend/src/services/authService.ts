import apiClient from "@/services/apiClient";

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export const authService = {
  async login(username: string, password: string): Promise<TokenPair> {
    const { data } = await apiClient.post<TokenPair>("/auth/login", { username, password });
    return data;
  },

  async register(username: string, email: string, password: string): Promise<void> {
    await apiClient.post("/auth/register", { username, email, password });
  },

  async logout(refreshToken: string): Promise<void> {
    await apiClient.post("/auth/logout", { refresh_token: refreshToken });
  },
};
