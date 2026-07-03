import { createContext, ReactNode, useContext, useEffect, useState } from "react";

import { authService } from "@/services/authService";
import { tokenStorage } from "@/utils/tokenStorage";

interface AuthContextValue {
  isAuthenticated: boolean | null; // null while the initial check is pending
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    setIsAuthenticated(tokenStorage.getAccessToken() !== null);
  }, []);

  async function login(username: string, password: string) {
    const tokens = await authService.login(username, password);
    tokenStorage.setTokens(tokens.access_token, tokens.refresh_token);
    setIsAuthenticated(true);
  }

  async function logout() {
    const refreshToken = tokenStorage.getRefreshToken();
    try {
      if (refreshToken) await authService.logout(refreshToken);
    } finally {
      tokenStorage.clear();
      setIsAuthenticated(false);
    }
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>{children}</AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
