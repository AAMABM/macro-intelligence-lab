import Plot from "react-plotly.js";
import { useQuery } from "@tanstack/react-query";
import { referenceApi } from "@/lib/reference";

interface MacroChartProps {
  indicatorCode: string;
  countryIso2?: string;
  title?: string;
}

// We removed 'title' from the destructuring because we don't use it in the chart layout
export function MacroChart({ indicatorCode, countryIso2 = "US" }: MacroChartProps) {
  const { data: seriesData, isLoading, isError } = useQuery({
    queryKey: ["series", indicatorCode, countryIso2],
    queryFn: () => referenceApi.getSeries(indicatorCode, countryIso2),
  });

  const { data: forecastData } = useQuery({
    queryKey: ["forecast", indicatorCode, countryIso2],
    queryFn: () => referenceApi.getForecast(indicatorCode, countryIso2),
    retry: false, // Don't break the chart if forecast fails
  });

  if (isLoading) {
    return <div className="flex flex-1 items-center justify-center text-sm text-text-muted animate-pulse">Loading chart...</div>;
  }

  if (isError || !seriesData) {
    return <div className="flex flex-1 items-center justify-center text-sm text-danger">Failed to load data.</div>;
  }

  // 1. Historical Data
  const xValues = seriesData.points.map((p) => p.period);
  const yValues = seriesData.points.map((p) => parseFloat(p.value));

  const plotData: Plotly.Data[] = [
    {
      x: xValues,
      y: yValues,
      type: "scatter",
      mode: "lines",
      name: "Historical", // <--- Here is the name!
      line: { color: "#3B82F6", width: 2 },
      fill: "tozeroy",
      fillcolor: "rgba(59, 130, 246, 0.1)",
    },
  ];

  // 2. Forecast Data (if available)
  if (forecastData && forecastData.points.length > 0) {
    const fX = forecastData.points.map((p) => p.period);
    const fY = forecastData.points.map((p) => p.yhat);
    const fUpper = forecastData.points.map((p) => p.yhatUpper);
    const fLower = forecastData.points.map((p) => p.yhatLower);

    // Confidence Interval Band
    plotData.push({
      x: [...fX, ...fX.slice().reverse()],
      y: [...fUpper, ...fLower.slice().reverse()],
      type: "scatter",
      mode: "lines",
      fill: "toself",
      fillcolor: "rgba(245, 158, 11, 0.15)", // Subtle amber fill
      line: { color: "transparent" },
      name: "80% CI",
      hoverinfo: "skip",
    });

    // Forecast Median Line
    plotData.push({
      x: fX,
      y: fY,
      type: "scatter",
      mode: "lines",
      name: "Forecast",
      line: { color: "#F59E0B", width: 2, dash: "dash" },
    });
  }

  return (
    <div className="w-full h-full">
      <Plot
        data={plotData}
        layout={{
          autosize: true,
          margin: { l: 50, r: 20, t: 20, b: 60 },
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
          font: { color: "#94A3B8", size: 11, family: "Inter" },
          xaxis: { showgrid: true, gridcolor: "#1E293B", zeroline: false, tickformat: "%Y" },
          yaxis: { showgrid: true, gridcolor: "#1E293B", zeroline: false },
          hovermode: "x unified",
          showlegend: false, // Hide legend to keep it clean
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: "100%", height: "100%" }}
        useResizeHandler={true}
      />
    </div>
  );
}