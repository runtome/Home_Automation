import { useTurnOff, useTurnOn } from "@/hooks/useDevices";
import { Device } from "@/types/device";

export default function DeviceCard({ device }: { device: Device }) {
  const turnOn = useTurnOn();
  const turnOff = useTurnOff();
  const pending = turnOn.isPending || turnOff.isPending;

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <div className="mb-1 flex items-center justify-between">
        <h3 className="font-semibold text-gray-900">{device.device_name}</h3>
        <span className="flex items-center gap-1.5 text-xs font-medium text-gray-500">
          <span
            className={`h-2.5 w-2.5 rounded-full ${device.online ? "bg-online" : "bg-offline"}`}
            aria-hidden
          />
          {device.online ? "Online" : "Offline"}
        </span>
      </div>
      <p className="mb-3 text-sm text-gray-500">{device.room}</p>
      <div className="mb-3 flex items-center gap-2">
        <span className="text-xs text-gray-500">Relay:</span>
        <span
          className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
            device.status === "ON"
              ? "bg-green-100 text-green-700"
              : device.status === "OFF"
                ? "bg-gray-100 text-gray-700"
                : "bg-yellow-100 text-yellow-700"
          }`}
        >
          {device.status}
        </span>
      </div>
      <div className="flex gap-2">
        <button
          onClick={() => turnOn.mutate(device.id)}
          disabled={pending}
          className="flex-1 rounded-md bg-green-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
        >
          ON
        </button>
        <button
          onClick={() => turnOff.mutate(device.id)}
          disabled={pending}
          className="flex-1 rounded-md bg-gray-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-gray-700 disabled:opacity-50"
        >
          OFF
        </button>
      </div>
    </div>
  );
}
