import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card } from "@/components/ui/Card";
import { useAuthStore } from "@/stores/auth";

export function RegisterPage() {
  const navigate = useNavigate();
  const register = useAuthStore((s) => s.register);
  const loading = useAuthStore((s) => s.status === "loading");
  const error = useAuthStore((s) => s.error);

  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [localError, setLocalError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLocalError(null);

    if (displayName.trim().length === 0) {
      setLocalError("Display name is required.");
      return;
    }
    if (password.length < 12) {
      setLocalError("Password must be at least 12 characters.");
      return;
    }

    try {
      await register(email, password, displayName.trim());
      navigate("/"); // Redirect to home on success
    } catch {
      // Error is handled by Zustand store
    }
  };

  const shownError = localError ?? error;

  return (
    <div className="mx-auto flex max-w-md flex-col gap-6 px-6 py-16">
      <div>
        <h1 className="text-2xl font-semibold text-text-primary">Create account</h1>
        <p className="mt-1 text-sm text-text-secondary">
          Free. No credit card. Access to the research terminal when it opens.
        </p>
      </div>

      <Card>
        <form className="flex flex-col gap-4" onSubmit={handleSubmit} noValidate>
          <Input
            label="Display name"
            type="text"
            autoComplete="name"
            required
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
          />
          <Input
            label="Email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <Input
            label="Password"
            type="password"
            autoComplete="new-password"
            required
            minLength={12}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <p className="text-xs text-text-muted">
            Minimum 12 characters. A strength check runs on the server.
          </p>

          {shownError && (
            <p role="alert" className="rounded-md border border-danger/40 bg-danger/10 px-3 py-2 text-sm text-danger">
              {shownError}
            </p>
          )}

          <Button type="submit" loading={loading}>
            Create account
          </Button>
        </form>
      </Card>

      <p className="text-center text-sm text-text-secondary">
        Already have an account?{" "}
        <Link to="/login" className="text-primary hover:underline">
          Sign in
        </Link>
      </p>
    </div>
  );
}