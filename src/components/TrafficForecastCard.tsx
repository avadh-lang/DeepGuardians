import { TrendingUp, TrendingDown, Minus, Radio } from "lucide-react";
import { AreaChart, Area, XAxis, YAxis, ResponsiveContainer, Tooltip } from "recharts";
import type { TrafficDataPoint, RouteStatus } from "@/hooks/useSimulation";

const StatusBadge = ({ status }: { status: string }) => {
  const colors = {
    heavy: "bg-destructive/20 text-destructive",
    moderate: "bg-warning/20 text-warning",
    light: "bg-success/20 text-success",
  };
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${colors[status as keyof typeof colors]}`}>
      {status}
    </span>
  );
};

interface Props {
  forecastData: TrafficDataPoint[];
  routes: RouteStatus[];
}

const TrafficForecastCard = ({ forecastData, routes }: Props) => {
  return (
    <div className="card-glass p-6 animate-slide-up-delay-1">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-foreground">Traffic Forecast</h3>
          <p className="text-sm text-muted-foreground">LSTM-predicted congestion levels</p>
        </div>
        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          <span className="flex items-center gap-1">
            <Radio className="w-3 h-3 text-primary animate-pulse" /> Live
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-primary" /> Actual
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-accent" /> Predicted
          </span>
        </div>
      </div>

      <div className="h-48 mb-6">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={forecastData}>
            <defs>
              <linearGradient id="colorCongestion" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="hsl(168, 80%, 50%)" stopOpacity={0.3} />
                <stop offset="95%" stopColor="hsl(168, 80%, 50%)" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorPredicted" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="hsl(270, 70%, 60%)" stopOpacity={0.3} />
                <stop offset="95%" stopColor="hsl(270, 70%, 60%)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis dataKey="time" stroke="hsl(215, 12%, 30%)" fontSize={10} tickLine={false} axisLine={false} />
            <YAxis stroke="hsl(215, 12%, 30%)" fontSize={10} tickLine={false} axisLine={false} />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(220, 18%, 10%)",
                border: "1px solid hsl(220, 14%, 18%)",
                borderRadius: "8px",
                fontSize: "12px",
              }}
            />
            <Area type="monotone" dataKey="congestion" stroke="hsl(168, 80%, 50%)" fill="url(#colorCongestion)" strokeWidth={2} animationDuration={800} />
            <Area type="monotone" dataKey="predicted" stroke="hsl(270, 70%, 60%)" fill="url(#colorPredicted)" strokeWidth={2} strokeDasharray="5 5" animationDuration={800} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="space-y-3">
        {routes.map((route) => (
          <div key={route.name} className="flex items-center justify-between p-3 rounded-lg bg-secondary/50 transition-all duration-500">
            <div className="flex items-center gap-3">
              <StatusBadge status={route.status} />
              <span className="text-sm font-medium text-foreground">{route.name}</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1 text-xs font-mono">
                {route.change > 0 ? <TrendingUp className="w-3 h-3 text-destructive" /> :
                 route.change < 0 ? <TrendingDown className="w-3 h-3 text-success" /> :
                 <Minus className="w-3 h-3 text-muted-foreground" />}
                <span className={route.change > 0 ? "text-destructive" : route.change < 0 ? "text-success" : "text-muted-foreground"}>
                  {route.change > 0 ? "+" : ""}{route.change}%
                </span>
              </span>
              <span className="text-sm font-mono text-foreground transition-all duration-500">{route.eta}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TrafficForecastCard;
