import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { CountryCard } from "@/components/data/CountryCard";
import { IndicatorRow } from "@/components/data/IndicatorRow";
import { referenceApi } from "@/lib/reference";

export function HomePage() {
  const { data: countriesData, isLoading: loadingCountries } = useQuery({
    queryKey: ["countries"],
    queryFn: referenceApi.getCountries,
  });

  const { data: indicatorsData, isLoading: loadingIndicators } = useQuery({
    queryKey: ["indicators"],
    queryFn: referenceApi.getIndicators,
  });

  return (
    <div className="mx-auto max-w-7xl px-6">
      {/* Hero */}
      <section className="grid gap-10 py-16 md:grid-cols-2 md:items-center md:py-24">
        <div>
          <p className="mb-3 text-xs font-medium uppercase tracking-wider text-primary">
            Macro Intelligence Lab
          </p>
          <h1 className="text-4xl font-semibold leading-tight text-text-primary sm:text-5xl">
            Economic Intelligence.
            <br />
            Market Insight.
            <br />
            Research-Driven Decisions.
          </h1>
          <p className="mt-6 max-w-xl text-base leading-relaxed text-text-secondary">
            Independent macro research on growth, inflation, rates, currencies,
            and country risk. Every forecast is scored in public.
          </p>
          <div className="mt-8 flex flex-wrap items-center gap-3">
            <Button disabled title="Weekly outlook publishing starts in Sprint 4">
              Read the weekly outlook →
            </Button>
            <Button variant="secondary" disabled title="Terminal opens in Sprint 4">
              Enter the terminal
            </Button>
          </div>
        </div>

        <Card className="min-h-[280px]">
          <div className="flex h-full min-h-[220px] flex-col items-center justify-center text-center">
            <p className="text-sm font-medium text-text-secondary">Featured chart</p>
            <p className="mt-2 max-w-xs text-xs text-text-muted">
              Yield curve and macro tiles will populate here in Sprint 3.
            </p>
          </div>
        </Card>
      </section>

      {/* Live Data Sections */}
      <section className="grid gap-6 py-12 md:grid-cols-2">
        
        {/* Countries */}
        <Card title="Country Intelligence">
          {loadingCountries ? (
            <p className="text-sm text-text-muted animate-pulse">Loading countries...</p>
          ) : (
            <div className="grid gap-3">
              {countriesData?.map((country) => (
                <CountryCard key={country.iso2} country={country} />
              ))}
            </div>
          )}
        </Card>

        {/* Indicators */}
        <Card title="Macroeconomic Indicators">
          {loadingIndicators ? (
            <p className="text-sm text-text-muted animate-pulse">Loading indicators...</p>
          ) : (
            <div className="flex flex-col">
              {indicatorsData?.slice(0, 6).map((indicator) => (
                <IndicatorRow key={indicator.code} indicator={indicator} />
              ))}
              <div className="mt-4 text-center">
                <Link to="/indicators" className="text-xs text-primary hover:underline">
                  View all {indicatorsData?.length} indicators →
                </Link>
              </div>
            </div>
          )}
        </Card>

      </section>

      {/* Trust strip */}
      <section
        aria-label="Forecast track record"
        className="border-y border-border py-5 mt-8"
      >
        <div className="flex flex-col items-center gap-1 text-center sm:flex-row sm:justify-center sm:gap-6 sm:text-left">
          <p className="text-sm text-text-secondary">
            <span className="font-mono tabular text-text-primary">0</span>{" "}
            forecasts published
          </p>
          <span className="hidden text-border-strong sm:inline">·</span>
          <p className="text-sm text-text-secondary">
            Median MAPE{" "}
            <span className="font-mono tabular text-text-primary">—</span>
          </p>
          <span className="hidden text-border-strong sm:inline">·</span>
          <p className="text-sm text-text-secondary">
            Scored against data vintages
          </p>
          <Link
            to="/methodology"
            className="text-sm text-primary hover:underline"
          >
            Methodology →
          </Link>
        </div>
        <p className="mt-2 text-center text-xs text-text-muted">
          The scorecard activates once the first forecasts are published in
          Sprint 4.
        </p>
      </section>

      {/* Economist strip */}
      <section className="border-t border-border py-12">
        <div className="max-w-3xl">
          <p className="text-xs font-medium uppercase tracking-wider text-text-muted">
            About the economist
          </p>
          <p className="mt-3 text-base leading-relaxed text-text-secondary">
            Macro Intelligence Lab is built and maintained by a single
            economist and engineer. The full profile, publications, and
            forecast track record will publish alongside the first research
            cycle.
          </p>
          <Link
            to="/about"
            className="mt-4 inline-block text-sm text-primary hover:underline"
          >
            Learn more →
          </Link>
        </div>
      </section>
    </div>
  );
}