import { Link } from "react-router-dom";
import { Button } from "@/components/ui/Button";

export function NotFoundPage() {
  return (
    <div className="mx-auto flex max-w-md flex-col items-start gap-6 px-6 py-24">
      <p className="text-xs font-medium uppercase tracking-wider text-text-muted">
        404
      </p>
      <h1 className="text-3xl font-semibold text-text-primary">
        This page does not exist.
      </h1>
      <p className="text-sm text-text-secondary">
        The link may be out of date, or the page may have moved.
      </p>
      <Link to="/">
        <Button variant="secondary">Back to home</Button>
      </Link>
    </div>
  );
}