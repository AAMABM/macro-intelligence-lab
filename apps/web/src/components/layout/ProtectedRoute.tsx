import { Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "@/stores/auth";

export function ProtectedRoute() {
  const status = useAuthStore((s) => s.status);

  // If the app is still loading the token on page refresh, show a loading spinner
  if (status === "idle" || status === "loading") {
    return (
      <div className="flex min-h-screen items-center justify-center bg-bg-base text-text-muted animate-pulse">
        Initializing Terminal...
      </div>
    );
  }

  // If the user is not authenticated, redirect to the login page
  if (status === "unauthenticated") {
    return <Navigate to="/login" replace />;
  }

  // If authenticated, render the child routes (the Terminal pages)
  return <Outlet />;
}