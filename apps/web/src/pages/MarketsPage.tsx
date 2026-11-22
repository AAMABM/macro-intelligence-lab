import { useQuery } from "@tanstack/react-query";
import { referenceApi } from "@/lib/reference";
import { Card } from "@/components/ui/Card";
import { MarketChart } from "@/components/data/MarketChart";

export function MarketsPage() {
  const { data: instruments, isLoading } = useQuery({
    queryKey: ["markets"],
    queryFn: referenceApi.getMarkets,
  });

  if (isLoading) {
    return <div className="p-12 text-center text-text-muted animate-pulse">Loading markets...</div>;
  }

  return (
    <div className="mx-auto max-w-7xl px-6 py-12">
      <h1 className="mb-2 text-3xl font-semibold text-text-primary">Market Intelligence</h1>
      <p className="mb-8 text-text-secondary">Live charts for major indices, commodities, and FX pairs.</p>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {instruments?.map((inst, index) => {
          // Alternate colors for a nicer look
          const colors = ["#10B981", "#F59E0B", "#3B82F6"]; 
          const color = colors[index % colors.length];
          
          return (
            <Card key={inst.symbol} title={inst.name} className="h-[350px]">
              <div className="flex-1 flex flex-col pt-2">
                <MarketChart symbol={inst.symbol} color={color} />
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}