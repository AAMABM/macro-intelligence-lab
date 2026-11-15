import type { HTMLAttributes, ReactNode } from "react";

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  action?: ReactNode;
}

export function Card({ title, action, className = "", children, ...rest }: CardProps) {
  return (
    <section
      className={[
        "rounded-lg border border-border bg-card",
        "shadow-[0_1px_0_#1E293B,0_8px_24px_-12px_#000]",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
      {...rest}
    >
      {(title || action) && (
        <header className="flex items-center justify-between border-b border-border px-4 py-3">
          {title && <h2 className="text-sm font-semibold text-text-primary">{title}</h2>}
          {action}
        </header>
      )}
      <div className="p-4">{children}</div>
    </section>
  );
}