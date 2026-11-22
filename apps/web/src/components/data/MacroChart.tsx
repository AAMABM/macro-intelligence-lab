import Plot from "react-plotly.js";
import { useQuery } from "@tanstack/react-query";
import { referenceApi } from "@/lib/reference";

interface MacroChartProps {
  indicatorCode: string;
  countryIso2?: string;
  title?: string;
}

export function MacroChart({ indicatorCode, countryIso2 = "US", title }: MacroChartProps) {
  const { data: seriesData, isLoading, isError } = useQuery({
    queryKey: ["series", indicatorCode, countryIso2],
    queryFn: () => referenceApi.getSeries(indicatorCode, countryIso2),
  });

  if (isLoading) {
    return (
      <div className="flex flex-1 items-center justify-center text-sm text-text-muted animate-pulse">
        Loading chart...
      </div>
    );
  }

  if (isError || !seriesData) {
    return (
      <div className="flex flex-1 items-center justify-center text-sm text-danger">
        Failed to load data.
      </div>
    );
  }

  const xValues = seriesData.points.map((p) => p.period);
  const yValues = seriesData.points.map((p) => parseFloat(p.value));

  return (
    <div className="w-full h-full relative">
      <Plot
        data={[
          {
            x: xValues,
            y: yValues,
            type: "scatter",
            mode: "lines",
            name: title || indicatorCode,
            line: { color: "#3B82F6", width: 2 },
            fill: "tozeroy",
            fillcolor: "rgba(59, 130, 246, 0.1)",
          },
        ]}
        layout={{
          autosize: true,
          margin: { l: 70, r: 20, t: 20, b: 70 }, // <-- Bigger margins
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
          font: { color: "#94A3B8", size: 11, family: "Inter" },
          xaxis: { 
            showgrid: true, 
            gridcolor: "#1E293B", 
            zeroline: false, 
            tickformat: "%Y",
            tickpadding: 10 // <-- Forces space between axis and text
          },
          yaxis: { 
            showgrid: true, 
            gridcolor: "#1E293B", 
            zeroline: false,
            tickpadding: 10 
          },
          hovermode: "x unified",
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%" }}
        useResizeHandler={true}
      />
    </div>
  );
}