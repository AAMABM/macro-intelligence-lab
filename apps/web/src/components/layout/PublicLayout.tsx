import { Outlet } from "react-router-dom";
import { TopNav } from "./TopNav";

export function PublicLayout() {
  return (
    <div className="flex min-h-screen flex-col">
      <TopNav />
      {/* TickerStrip slot — reserved for Sprint 2 */}
      <main className="flex-1">
        <Outlet />
      </main>
      <footer className="border-t border-border">
        <div className="mx-auto flex max-w-7xl flex-col gap-2 px-6 py-8 text-sm text-text-muted sm:flex-row sm:items-center sm:justify-between">
          <p>© {new Date().getFullYear()} Macro Intelligence Lab</p>
          <p className="text-xs">
            Economic Intelligence. Market Insight. Research-Driven Decisions.
          </p>
        </div>
      </footer>
    </div>
  );
}