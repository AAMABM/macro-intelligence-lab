import type { HTMLAttributes, ReactNode } from "react";

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  action?: ReactNode;
}

export function Card({ title, action, className = "", children, ...rest }: CardProps) {
  return (
    <section
      className={[
        "rounded-lg border border-border bg-card flex flex-col", // Added flex flex-col
        "shadow-[0_1px_0_#1E293B,0_8px_24px_-12px_#000]",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
      {...rest}
    >
      {(title || action) && (
        <header className="flex shrink-0 items-center justify-between border-b border-border px-4 py-3">
          {title && <h2 className="text-sm font-semibold text-text-primary">{title}</h2>}
          {action}
        </header>
      )}
      {/* Added flex-1 and flex-col so the content area grows to fill the fixed height */}
      <div className="flex-1 flex flex-col p-4">
        {children}
      </div>
    </section>
  );
}