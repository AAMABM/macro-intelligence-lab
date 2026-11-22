import Plot from "react-plotly.js";
import { useQuery } from "@tanstack/react-query";
import { referenceApi } from "@/lib/reference";

interface MarketChartProps {
  symbol: string;
  color?: string;
}

export function MarketChart({ symbol, color = "#10B981" }: MarketChartProps) {
  const { data: seriesData, isLoading, isError } = useQuery({
    queryKey: ["market-series", symbol],
    queryFn: () => referenceApi.getMarketSeries(symbol),
  });

  if (isLoading) {
    return <div className="flex flex-1 items-center justify-center text-sm text-text-muted animate-pulse">Loading chart...</div>;
  }

  if (isError || !seriesData) {
    return <div className="flex flex-1 items-center justify-center text-sm text-danger">Failed to load data.</div>;
  }

  const xValues = seriesData.points.map((p) => p.priceDate);
  const yValues = seriesData.points.map((p) => parseFloat(p.closePrice));

  return (
    <div className="flex-1 w-full relative">
      <div className="absolute inset-0">
        <Plot
          data={[
            {
              x: xValues,
              y: yValues,
              type: "scatter",
              mode: "lines",
              name: seriesData.name,
              line: { color, width: 2 },
              fill: "tozeroy",
              fillcolor: color === "#10B981" ? "rgba(16, 185, 129, 0.1)" : "rgba(245, 158, 11, 0.1)",
            },
          ]}
          layout={{
            autosize: true,
            margin: { l: 40, r: 20, t: 10, b: 40 },
            paper_bgcolor: "transparent",
            plot_bgcolor: "transparent",
            font: { color: "#94A3B8", size: 11, family: "Inter" },
            xaxis: { showgrid: true, gridcolor: "#1E293B", zeroline: false, tickformat: "%b %y" },
            yaxis: { showgrid: true, gridcolor: "#1E293B", zeroline: false },
            hovermode: "x unified",
          }}
          config={{ displayModeBar: false }}
          style={{ width: "100%", height: "100%" }}
          useResizeHandler={true}
        />
      </div>
    </div>
  );
}