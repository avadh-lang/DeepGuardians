import { Car, MapPin, Clock, TrendingDown } from "lucide-react";
import type { ParkingSpot } from "@/hooks/useSimulation";

interface Props {
  parking: ParkingSpot[];
}

const ParkingIntelCard = ({ parking }: Props) => {
  const getAvailabilityColor = (available: number, total: number) => {
    const ratio = available / total;
    if (ratio > 0.3) return "text-success";
    if (ratio > 0.1) return "text-warning";
    return "text-destructive";
  };

  const getBarColor = (available: number, total: number) => {
    const ratio = available / total;
    if (ratio > 0.3) return "bg-success";
    if (ratio > 0.1) return "bg-warning";
    return "bg-destructive";
  };

  return (
    <div className="card-glass p-6 animate-slide-up-delay-3">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-foreground">Parking Intelligence</h3>
          <p className="text-sm text-muted-foreground">Real-time availability near destination</p>
        </div>
        <div className="p-2 rounded-lg bg-accent/10 glow-accent">
          <Car className="w-5 h-5 text-accent" />
        </div>
      </div>

      <div className="space-y-4">
        {parking.map((spot, i) => (
          <div key={i} className="p-4 rounded-lg bg-secondary/30 border border-border/50 hover:border-accent/30 transition-all duration-500 cursor-pointer">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h4 className="text-sm font-semibold text-foreground">{spot.name}</h4>
                <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{spot.distance}</span>
                  <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{spot.eta}</span>
                  <span>{spot.price}</span>
                </div>
              </div>
              <div className="text-right">
                <span className={`text-xl font-mono font-bold transition-all duration-500 ${getAvailabilityColor(spot.available, spot.total)}`}>
                  {spot.available}
                </span>
                <span className="text-xs text-muted-foreground">/{spot.total}</span>
              </div>
            </div>
            <div className="w-full h-1.5 rounded-full bg-secondary">
              <div
                className={`h-full rounded-full transition-all duration-700 ${getBarColor(spot.available, spot.total)}`}
                style={{ width: `${(spot.available / spot.total) * 100}%` }}
              />
            </div>
            {spot.trend === "critical" && (
              <div className="flex items-center gap-1 mt-2 text-xs text-destructive animate-pulse">
                <TrendingDown className="w-3 h-3" />
                <span>Filling fast — predicted full in 15 min</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ParkingIntelCard;
