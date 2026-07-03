import { useAuth } from "@/hooks/useAuth";

export default function Navbar() {
  const { logout } = useAuth();

  return (
    <header className="flex items-center justify-between border-b border-gray-200 bg-white px-6 py-4">
      <h1 className="text-lg font-semibold text-gray-900">Home Automation Platform</h1>
      <button onClick={() => logout()} className="text-sm font-medium text-gray-600 hover:text-gray-900">
        Log out
      </button>
    </header>
  );
}
