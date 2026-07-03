import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

import { API_URL } from "@/utils/constants";
import { tokenStorage } from "@/utils/tokenStorage";

const apiClient = axios.create({ baseURL: API_URL });

apiClient.interceptors.request.use((config) => {
  const token = tokenStorage.getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let refreshPromise: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  const refreshToken = tokenStorage.getRefreshToken();
  if (!refreshToken) throw new Error("no refresh token available");

  const { data } = await axios.post(`${API_URL}/auth/refresh`, { refresh_token: refreshToken });
  tokenStorage.setTokens(data.access_token, data.refresh_token);
  return data.access_token as string;
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;

    if (error.response?.status !== 401 || !original || original._retry) {
      throw error;
    }
    original._retry = true;

    try {
      refreshPromise ??= refreshAccessToken();
      const newAccessToken = await refreshPromise;
      original.headers.Authorization = `Bearer ${newAccessToken}`;
      return apiClient(original);
    } catch (refreshError) {
      tokenStorage.clear();
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
      throw refreshError;
    } finally {
      refreshPromise = null;
    }
  }
);

export default apiClient;
