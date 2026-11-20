import Plot from "react-plotly.js";
import { useQuery } from "@tanstack/react-query";
import { referenceApi } from "@/lib/reference";

export function CpiChart() {
  const { data: seriesData, isLoading, isError } = useQuery({
    queryKey: ["series", "CPI_YOY", "US"],
    queryFn: () => referenceApi.getSeries("CPI_YOY", "US"),
  });

  if (isLoading) {
    return (
      <div className="flex h-full min-h-[300px] items-center justify-center text-sm text-text-muted animate-pulse">
        Loading historical data...
      </div>
    );
  }

  if (isError || !seriesData) {
    return (
      <div className="flex h-full min-h-[300px] items-center justify-center text-sm text-danger">
        Failed to load chart data.
      </div>
    );
  }

  // Parse the data for Plotly
  const xValues = seriesData.points.map((p) => p.period);
  const yValues = seriesData.points.map((p) => parseFloat(p.value));

  return (
    <div className="h-full min-h-[300px] w-full">
      <Plot
        data={[
          {
            x: xValues,
            y: yValues,
            type: "scatter",
            mode: "lines",
            name: "US CPI",
            line: { color: "#3B82F6", width: 2 }, // Matches your primary blue
            fill: "tozeroy",
            fillcolor: "rgba(59, 130, 246, 0.1)", // Subtle blue fill under the line
          },
        ]}
        layout={{
          autosize: true,
          margin: { l: 40, r: 20, t: 10, b: 30 },
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
          font: { color: "#94A3B8", size: 11, family: "Inter" },
          xaxis: {
            showgrid: true,
            gridcolor: "#1E293B",
            zeroline: false,
            tickformat: "%Y", // Show only the year
          },
          yaxis: {
            showgrid: true,
            gridcolor: "#1E293B",
            zeroline: false,
          },
          hovermode: "x unified",
        }}
        config={{ displayModeBar: false }} // Hides the Plotly toolbar for a cleaner look
        style={{ width: "100%", height: "100%" }}
      />
    </div>
  );
}