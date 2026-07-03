import { Log } from "@/types/log";

export default function RecentActivity({ logs }: { logs: Log[] }) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 font-semibold text-gray-900">Recent Activity</h3>
      {logs.length === 0 ? (
        <p className="text-sm text-gray-500">No activity yet.</p>
      ) : (
        <ul className="space-y-2">
          {logs.map((log) => (
            <li key={log.id} className="flex justify-between text-sm">
              <span className="text-gray-700">{log.message ?? log.action}</span>
              <span className="whitespace-nowrap text-gray-400">
                {new Date(log.created_at).toLocaleTimeString()}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
