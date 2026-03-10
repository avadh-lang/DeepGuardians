import { Clock, Route, Car, Zap } from "lucide-react";
import type { StatsData } from "@/hooks/useSimulation";

interface Props {
  stats: StatsData;
}

const StatsBar = ({ stats }: Props) => {
  const items = [
    { icon: Clock, label: "Avg. Commute", value: `${stats.avgCommute} min`, change: `-${Math.max(1, Math.round((34 - stats.avgCommute) / 34 * 100))}%`, positive: stats.avgCommute <= 34 },
    { icon: Route, label: "Routes Analyzed", value: stats.routesAnalyzed.toLocaleString(), change: "+live", positive: true },
    { icon: Car, label: "Parking Found", value: `${stats.parkingFound}%`, change: "+3.1%", positive: true },
    { icon: Zap, label: "AI Accuracy", value: `${stats.aiAccuracy}%`, change: "+1.2%", positive: true },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 animate-slide-up">
      {items.map((stat, i) => (
        <div key={i} className="card-glass p-4 flex items-center gap-4">
          <div className="p-2.5 rounded-lg bg-primary/10">
            <stat.icon className="w-5 h-5 text-primary" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground">{stat.label}</p>
            <div className="flex items-baseline gap-2">
              <span className="text-xl font-bold font-mono text-foreground transition-all duration-500">{stat.value}</span>
              <span className={`text-xs font-mono ${stat.positive ? "text-success" : "text-destructive"}`}>
                {stat.change}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default StatsBar;
