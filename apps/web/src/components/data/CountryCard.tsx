import type { CountrySummary } from "@mil/types";

export function CountryCard({ country }: { country: CountrySummary }) {
  return (
    <div className="flex items-center gap-4 rounded-lg border border-border bg-card p-4 shadow-sm">
      <div className="text-3xl">{country.flagEmoji || "🌐"}</div>
      <div>
        <h3 className="font-semibold text-text-primary">{country.name}</h3>
        <p className="text-xs text-text-secondary">
          {country.regionCode || "Global"} • {country.currencyCode || "N/A"}
        </p>
      </div>
    </div>
  );
}