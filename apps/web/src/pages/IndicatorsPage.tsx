import { useQuery } from "@tanstack/react-query";
import { referenceApi } from "@/lib/reference";
import { IndicatorRow } from "@/components/data/IndicatorRow";
import { Card } from "@/components/ui/Card";

export function IndicatorsPage() {
  const { data: indicators, isLoading } = useQuery({ queryKey: ["indicators"], queryFn: referenceApi.getIndicators });

  return (
    <div className="mx-auto max-w-4xl px-6 py-12">
      <h1 className="mb-8 text-3xl font-semibold text-text-primary">Macro Indicators</h1>
      <Card>
        {isLoading ? <p className="text-text-muted p-4">Loading...</p> : (
          <div className="flex flex-col p-4">
            {indicators?.map((i) => <IndicatorRow key={i.code} indicator={i} />)}
          </div>
        )}
      </Card>
    </div>
  );
}