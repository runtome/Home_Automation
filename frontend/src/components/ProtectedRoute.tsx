import { useRouter } from "next/router";
import { ReactNode, useEffect } from "react";

import { useAuth } from "@/hooks/useAuth";

export default function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated === false) {
      router.replace("/login");
    }
  }, [isAuthenticated, router]);

  if (isAuthenticated !== true) {
    return (
      <div className="flex min-h-screen items-center justify-center text-gray-500">Loading...</div>
    );
  }

  return <>{children}</>;
}
