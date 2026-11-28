import { useQuery } from "@tanstack/react-query";
import { referenceApi } from "@/lib/reference";
import { Card } from "@/components/ui/Card";
import { CountryCard } from "@/components/data/CountryCard";
import { Link } from "react-router-dom";

export function TerminalCountries() {
  const { data: countries, isLoading } = useQuery({ queryKey: ["countries"], queryFn: referenceApi.getCountries });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-text-primary">Countries</h1>
        <p className="text-sm text-text-secondary">Select a country to view detailed intelligence.</p>
      </div>

      {isLoading ? (
        <div className="text-text-muted">Loading countries...</div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {countries?.map((c) => (
            <Link key={c.iso2} to={`/countries/${c.iso2}`} className="transition-transform hover:-translate-y-1">
              <Card className="p-0 overflow-hidden border-border hover:border-primary/50">
                <CountryCard country={c} />
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}