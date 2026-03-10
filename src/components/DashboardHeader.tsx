import { Navigation, Bell, User, Search, MapPin, Radio } from "lucide-react";
import TrafficMap from "../components/TrafficMap";

interface Props {
  lastUpdated?: Date;
}

function Dashboard() {
  return (
    <div>
      <TrafficMap />
    </div>
  );
}

const DashboardHeader = ({ lastUpdated }: Props) => {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/50 bg-background/80 backdrop-blur-xl">
      <div className="container flex items-center justify-between h-16 px-6">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary/10 glow-primary">
            <Navigation className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight">
              <span className="text-gradient-primary">NavAI</span>
            </h1>
            <p className="text-[10px] text-muted-foreground -mt-0.5 tracking-widest uppercase">Predictive Mobility</p>
          </div>
        </div>

        <div className="hidden md:flex items-center gap-2 px-4 py-2 rounded-lg bg-secondary/50 border border-border/50 w-96">
          <Search className="w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search destination or route..."
            className="bg-transparent text-sm text-foreground placeholder:text-muted-foreground outline-none w-full"
          />
          <div className="flex items-center gap-1 text-xs text-muted-foreground bg-secondary px-2 py-0.5 rounded">
            <MapPin className="w-3 h-3" /> Mumbai
          </div>
        </div>

        <div className="flex items-center gap-3">
          {lastUpdated && (
            <div className="hidden md:flex items-center gap-1.5 text-xs text-muted-foreground px-3 py-1.5 rounded-lg bg-secondary/50 border border-border/50">
              <Radio className="w-3 h-3 text-primary animate-pulse" />
              <span>Live</span>
              <span className="text-muted-foreground/60">·</span>
              <span className="font-mono">{lastUpdated.toLocaleTimeString()}</span>
            </div>
          )}
          <button className="relative p-2 rounded-lg hover:bg-secondary/50 transition-colors">
            <Bell className="w-5 h-5 text-muted-foreground" />
            <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-primary animate-pulse-glow" />
          </button>
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center">
            <User className="w-4 h-4 text-primary-foreground" />
          </div>
        </div>
      </div>
    </header>
  );
};

export default DashboardHeader;
