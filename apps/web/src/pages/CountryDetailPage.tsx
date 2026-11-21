import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { referenceApi } from "@/lib/reference";
import { Card } from "@/components/ui/Card";
import { MacroChart } from "@/components/data/MacroChart";

export function CountryDetailPage() {
  const { iso2 } = useParams<{ iso2: string }>();
  const { data: country, isLoading } = useQuery({
    queryKey: ["country", iso2],
    queryFn: () => referenceApi.getCountryDetail(iso2!),
    enabled: !!iso2,
  });

  if (isLoading) return <div className="p-12 text-center text-text-muted">Loading...</div>;
  if (!country) return <div className="p-12 text-center text-danger">Country not found.</div>;

  return (
    <div className="mx-auto max-w-7xl px-6 py-12">
      <Link to="/countries" className="text-sm text-primary hover:underline mb-6 inline-block">← Back to Countries</Link>
      
      <div className="mb-8 flex items-center gap-4">
        <span className="text-5xl">{country.flagEmoji}</span>
        <div>
          <h1 className="text-3xl font-semibold text-text-primary">{country.name}</h1>
          <p className="text-text-secondary">{country.regionName} • {country.currencyName} ({country.currencyCode})</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card title="Consumer Price Index" className="h-[400px]">
          <MacroChart indicatorCode="CPI_YOY" countryIso2={country.iso2} title="Inflation" />
        </Card>
        <Card title="Unemployment Rate" className="h-[400px]">
          <MacroChart indicatorCode="UNEMPLOYMENT" countryIso2={country.iso2} title="Unemployment" />
        </Card>
      </div>
    </div>
  );
}