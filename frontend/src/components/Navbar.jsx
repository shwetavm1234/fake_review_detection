import { Link, useLocation, useNavigate } from "react-router-dom";
import { LogOut } from "lucide-react";
import { API_URL, useAuth } from "../context/AuthContext";

export default function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, setUser } = useAuth();
  const links = [["Home", "/"], ["Detect Review", "/detect"], ["Upload File", "/upload"], ["History", "/history"]];

  async function handleLogout() {
    try {
      await fetch(`${API_URL}/auth/logout`, { method: "POST", credentials: "include" });
    } finally {
      setUser(null);
      navigate("/login", { replace: true });
    }
  }

  return (
    <header className="mx-auto flex w-full max-w-7xl flex-wrap items-center justify-between gap-3 px-6 py-4">
      <span className="text-sm font-bold tracking-wider text-violet-300">FAKE REVIEW DETECTION</span>
      <nav className="flex flex-wrap items-center gap-2 sm:gap-4">
        {links.map(([label, path]) => <Link key={path} to={path} className={`rounded-md px-3 py-2 text-sm font-medium transition ${location.pathname === path ? "bg-violet-900/30 text-violet-400" : "text-gray-300 hover:text-violet-400"}`}>{label}</Link>)}
        <span className="hidden text-xs text-gray-400 md:inline">Hi, {user?.name}</span>
        <button type="button" onClick={handleLogout} className="flex items-center gap-2 rounded-lg border border-gray-700 px-3 py-2 text-sm text-gray-300 hover:border-violet-500 hover:text-white"><LogOut size={15} /> Logout</button>
      </nav>
    </header>
  );
}
