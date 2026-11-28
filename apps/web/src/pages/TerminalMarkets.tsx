import { useQuery } from "@tanstack/react-query";
import { referenceApi } from "@/lib/reference";
import { Card } from "@/components/ui/Card";
import { MarketChart } from "@/components/data/MarketChart";

export function TerminalMarkets() {
  const { data: instruments, isLoading } = useQuery({
    queryKey: ["markets"],
    queryFn: referenceApi.getMarkets,
  });

  if (isLoading) return <div className="p-8 text-text-muted">Loading markets...</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-text-primary">Markets</h1>
        <p className="text-sm text-text-secondary">Live pricing for major global assets.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {instruments?.map((inst, index) => {
          const colors = ["#10B981", "#F59E0B", "#3B82F6"];
          const color = colors[index % colors.length];
          
          return (
            <Card key={inst.symbol} title={inst.name} className="h-[350px] flex flex-col overflow-hidden">
              <div className="flex-1 w-full relative pt-2">
                <MarketChart symbol={inst.symbol} color={color} />
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}