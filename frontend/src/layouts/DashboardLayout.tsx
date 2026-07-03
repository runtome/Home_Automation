import { ReactNode } from "react";

import Navbar from "@/components/Navbar";
import { useDeviceSocket } from "@/hooks/useDeviceSocket";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  useDeviceSocket(true);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="mx-auto max-w-6xl space-y-6 px-6 py-6">{children}</main>
    </div>
  );
}
