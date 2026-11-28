import { Card } from "@/components/ui/Card";
import { MacroChart } from "@/components/data/MacroChart";

export function TerminalMacro() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary">Macroeconomics</h1>
          <p className="text-sm text-text-secondary">Key US economic indicators.</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="h-[400px] flex flex-col overflow-hidden" title="US Inflation (CPI YoY)">
          <div className="flex-1 w-full relative pt-2">
            <MacroChart indicatorCode="CPI_YOY" countryIso2="US" />
          </div>
        </Card>

        <Card className="h-[400px] flex flex-col overflow-hidden" title="US Real GDP Growth (YoY)">
          <div className="flex-1 w-full relative pt-2">
            <MacroChart indicatorCode="GDP_REAL_YOY" countryIso2="US" />
          </div>
        </Card>

        <Card className="h-[400px] flex flex-col overflow-hidden" title="US Unemployment Rate">
          <div className="flex-1 w-full relative pt-2">
            <MacroChart indicatorCode="UNEMPLOYMENT" countryIso2="US" />
          </div>
        </Card>
        
        <Card className="h-[400px] flex flex-col overflow-hidden" title="US Policy Rate">
          <div className="flex-1 w-full relative pt-2">
            <MacroChart indicatorCode="POLICY_RATE" countryIso2="US" />
          </div>
        </Card>
      </div>
    </div>
  );
}