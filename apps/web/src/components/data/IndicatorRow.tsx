import type { IndicatorSummary } from "@mil/types";

export function IndicatorRow({ indicator }: { indicator: IndicatorSummary }) {
  return (
    <div className="flex items-center justify-between border-b border-border py-3 last:border-0">
      <div>
        <p className="text-sm font-medium text-text-primary">{indicator.name}</p>
        <p className="text-xs text-text-muted">{indicator.code}</p>
      </div>
      <div className="text-right">
        <span className="inline-flex items-center rounded-full bg-inset px-2.5 py-0.5 text-xs font-medium text-text-secondary">
          {indicator.category}
        </span>
        <p className="mt-1 text-xs text-text-muted">{indicator.unit || "Index"}</p>
      </div>
    </div>
  );
}