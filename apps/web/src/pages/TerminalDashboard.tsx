import { useQuery } from "@tanstack/react-query";
import { referenceApi } from "@/lib/reference";
import { Card } from "@/components/ui/Card";
import { MacroChart } from "@/components/data/MacroChart";
import { MarketChart } from "@/components/data/MarketChart";
import { CountryCard } from "@/components/data/CountryCard";
import { IndicatorRow } from "@/components/data/IndicatorRow";
import { Link } from "react-router-dom";

export function TerminalDashboard() {
  const { data: countries } = useQuery({ queryKey: ["countries"], queryFn: referenceApi.getCountries });
  const { data: indicators } = useQuery({ queryKey: ["indicators"], queryFn: referenceApi.getIndicators });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-text-primary">Terminal Dashboard</h1>
        <p className="text-sm text-text-secondary">Global macro and market overview.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Macro Chart */}
        <Card className="h-[420px] flex flex-col overflow-hidden" title="US Inflation (CPI YoY)">
          <div className="flex-1 w-full relative">
            <MacroChart indicatorCode="CPI_YOY" countryIso2="US" />
          </div>
        </Card>

        {/* Market Chart */}
        <Card className="h-[420px] flex flex-col overflow-hidden" title="S&P 500 (2Y)">
          <div className="flex-1 w-full relative">
            <MarketChart symbol="^GSPC" color="#10B981" />
          </div>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Top Countries */}
        <Card title="Key Countries">
          <div className="grid gap-3 pt-2">
            {countries?.slice(0, 4).map((c) => (
              <Link key={c.iso2} to={`/terminal/countries`}>
                <CountryCard country={c} />
              </Link>
            ))}
            <Link to="/terminal/countries" className="text-xs text-primary hover:underline mt-2 block">
              View all countries →
            </Link>
          </div>
        </Card>

        {/* Top Indicators */}
        <Card title="Key Indicators">
          <div className="flex flex-col pt-2">
            {indicators?.slice(0, 5).map((i) => (
              <IndicatorRow key={i.code} indicator={i} />
            ))}
            <Link to="/terminal/macro" className="text-xs text-primary hover:underline mt-2 block">
              View all indicators →
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}