import DeviceCard from "@/components/DeviceCard";
import { Device } from "@/types/device";

export default function DeviceGrid({ devices }: { devices: Device[] }) {
  if (devices.length === 0) {
    return <p className="text-sm text-gray-500">No devices registered yet.</p>;
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {devices.map((device) => (
        <DeviceCard key={device.id} device={device} />
      ))}
    </div>
  );
}
