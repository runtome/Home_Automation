import Head from "next/head";

import DeviceGrid from "@/components/DeviceGrid";
import ProtectedRoute from "@/components/ProtectedRoute";
import RecentActivity from "@/components/RecentActivity";
import StatWidget from "@/components/StatWidget";
import { useDevices } from "@/hooks/useDevices";
import { useLogs } from "@/hooks/useLogs";
import DashboardLayout from "@/layouts/DashboardLayout";

function DashboardContent() {
  const { data: devices = [] } = useDevices();
  const { data: logs = [] } = useLogs();

  const onlineCount = devices.filter((d) => d.online).length;
  const offlineCount = devices.length - onlineCount;

  return (
    <>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatWidget label="Online Devices" value={onlineCount} />
        <StatWidget label="Offline Devices" value={offlineCount} />
        <StatWidget label="Recent Activities" value={logs.length} />
      </div>

      <section>
        <h2 className="mb-3 text-lg font-semibold text-gray-900">Devices</h2>
        <DeviceGrid devices={devices} />
      </section>

      <RecentActivity logs={logs} />
    </>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <Head>
        <title>Dashboard - Home Automation</title>
      </Head>
      <DashboardLayout>
        <DashboardContent />
      </DashboardLayout>
    </ProtectedRoute>
  );
}
