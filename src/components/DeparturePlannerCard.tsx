import { Clock, Navigation, Zap, ChevronRight } from "lucide-react";
import type { DepartureSuggestion } from "@/hooks/useSimulation";

interface Props {
  departures: DepartureSuggestion[];
}

const DeparturePlannerCard = ({ departures }: Props) => {
  return (
    <div className="card-glass p-6 animate-slide-up-delay-2">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-foreground">Smart Departure Planner</h3>
          <p className="text-sm text-muted-foreground">AI-optimized departure windows</p>
        </div>
        <div className="p-2 rounded-lg bg-primary/10 glow-primary">
          <Clock className="w-5 h-5 text-primary" />
        </div>
      </div>

      <div className="p-4 rounded-lg bg-secondary/30 border border-border/50 mb-4">
        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
          <Navigation className="w-4 h-4" />
          <span>Andheri → BKC</span>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span>Tomorrow, March 11</span>
          <span>•</span>
          <span>Meeting at 9:00 AM</span>
        </div>
      </div>

      <div className="space-y-3">
        {departures.map((s, i) => (
          <div
            key={i}
            className={`relative p-4 rounded-lg border transition-all duration-500 cursor-pointer hover:border-primary/50 ${
              s.optimal
                ? "bg-primary/5 border-primary/30 glow-primary"
                : "bg-secondary/30 border-border/50"
            }`}
          >
            {s.optimal && (
              <div className="absolute -top-2 right-3 px-2 py-0.5 rounded-full bg-primary text-primary-foreground text-[10px] font-semibold flex items-center gap-1">
                <Zap className="w-3 h-3" /> OPTIMAL
              </div>
            )}
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-3 mb-1">
                  <span className="text-lg font-semibold font-mono text-foreground">{s.time}</span>
                  <span className="text-sm text-muted-foreground">→ {s.duration}</span>
                </div>
                <p className="text-xs text-muted-foreground">{s.route}</p>
              </div>
              <div className="flex items-center gap-3">
                {s.savings !== "0 min" && (
                  <span className="text-xs font-medium text-success bg-success/10 px-2 py-1 rounded-full">
                    Save {s.savings}
                  </span>
                )}
                <div className="text-right">
                  <div className="text-xs text-muted-foreground">Confidence</div>
                  <div className="text-sm font-mono font-semibold text-foreground">{s.confidence}%</div>
                </div>
                <ChevronRight className="w-4 h-4 text-muted-foreground" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DeparturePlannerCard;
