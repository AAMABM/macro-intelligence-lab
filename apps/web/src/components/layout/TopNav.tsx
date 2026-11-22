import { Link, NavLink, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { useAuthStore } from "@/stores/auth";

const linkClass = "text-sm text-text-secondary hover:text-text-primary transition-colors";

export function TopNav() {
  const navigate = useNavigate();
  const { user, status, logout } = useAuthStore();
  const isAuthed = status === "authenticated" && user !== null;

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-bg-base/95 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-7xl items-center gap-6 px-6">
        <Link to="/" className="flex items-center gap-2">
          <span aria-hidden="true" className="text-primary">◈</span>
          <span className="text-sm font-semibold tracking-wide text-text-primary">
            MACRO INTELLIGENCE LAB
          </span>
        </Link>

        <nav className="hidden items-center gap-6 md:flex" aria-label="Primary">
          <NavLink to="/research" className={linkClass}>Research</NavLink>
          <NavLink to="/reports" className={linkClass}>Reports</NavLink>
          <NavLink to="/countries" className={linkClass}>Countries</NavLink>
          <NavLink to="/markets" className={linkClass}>Markets</NavLink>
          <NavLink to="/methodology" className={linkClass}>Methodology</NavLink>
          <NavLink to="/about" className={linkClass}>About</NavLink>
        </nav>

        <div className="ml-auto flex items-center gap-3">
          {isAuthed ? (
            <>
              <Link to="/terminal" className="hidden sm:block">
                <Button size="sm" className="bg-primary/20 text-primary hover:bg-primary/30">
                  Terminal
                </Button>
              </Link>
              <span className="hidden text-sm text-text-secondary sm:inline">
                {user?.displayName}
              </span>
              <Button variant="secondary" size="sm" onClick={handleLogout}>
                Sign out
              </Button>
            </>
          ) : (
            <>
              <Link to="/login" className={linkClass}>Sign in</Link>
              <Link to="/register">
                <Button size="sm">Sign up</Button>
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}