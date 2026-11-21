import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { referenceApi } from "@/lib/reference";
import { CountryCard } from "@/components/data/CountryCard";

export function CountriesPage() {
  const { data: countries, isLoading } = useQuery({ queryKey: ["countries"], queryFn: referenceApi.getCountries });

  return (
    <div className="mx-auto max-w-7xl px-6 py-12">
      <h1 className="mb-8 text-3xl font-semibold text-text-primary">Country Intelligence</h1>
      {isLoading ? <p className="text-text-muted">Loading...</p> : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {countries?.map((c) => (
            <Link key={c.iso2} to={`/countries/${c.iso2}`} className="transition-transform hover:-translate-y-1">
              <CountryCard country={c} />
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}