import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/auth";

const navItems = [
  { name: "Dashboard", path: "/terminal/dashboard", icon: "▦" },
  { name: "Macroeconomics", path: "/terminal/macro", icon: "▤" },
  { name: "Markets", path: "/terminal/markets", icon: "⌁" },
  { name: "Countries", path: "/terminal/countries", icon: "◍" },
];

export function TerminalLayout() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  return (
    <div className="flex h-screen w-full bg-bg-base text-text-primary">
      {/* SIDEBAR */}
      <aside className="flex w-64 flex-col border-r border-border bg-card">
        <div className="flex h-16 items-center border-b border-border px-6">
          <Link to="/" className="flex items-center gap-2">
            <span aria-hidden="true" className="text-primary">◈</span>
            <span className="text-sm font-semibold tracking-wide">MIL TERMINAL</span>
          </Link>
        </div>

        <nav className="flex-1 space-y-1 p-4">
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors ${
                  isActive
                    ? "bg-primary/10 font-medium text-primary"
                    : "text-text-secondary hover:bg-elevated hover:text-text-primary"
                }`
              }
            >
              <span className="text-lg">{item.icon}</span>
              {item.name}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-border p-4">
          <Link to="/" className="mb-4 block text-xs text-text-muted hover:text-text-primary">
            ← Back to Public Site
          </Link>
          <div className="flex items-center justify-between">
            <div className="truncate text-sm font-medium">
              {user?.displayName || "Analyst"}
            </div>
            <button
              onClick={handleLogout}
              className="text-xs text-danger hover:underline"
            >
              Sign out
            </button>
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT AREA */}
      <main className="flex flex-1 flex-col overflow-hidden">
        {/* TOP BAR */}
        <header className="flex h-16 items-center justify-between border-b border-border bg-card px-6">
          <div className="flex items-center gap-4 text-sm text-text-secondary">
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-success animate-pulse"></span>
              Live Data
            </span>
            <span className="hidden sm:inline">|</span>
            <span className="hidden sm:inline">Role: {user?.role}</span>
          </div>
          <div className="text-sm text-text-secondary">
            {new Date().toLocaleDateString("en-US", {
              weekday: "long",
              year: "numeric",
              month: "long",
              day: "numeric",
            })}
          </div>
        </header>

        {/* PAGE CONTENT (Scrollable) */}
        <div className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
}