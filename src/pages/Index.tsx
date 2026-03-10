import DashboardHeader from "@/components/DashboardHeader";
import StatsBar from "@/components/StatsBar";
import MapPreview from "@/components/MapPreview";
import TrafficForecastCard from "@/components/TrafficForecastCard";
import DeparturePlannerCard from "@/components/DeparturePlannerCard";
import ParkingIntelCard from "@/components/ParkingIntelCard";
import PersonalizedInsightsCard from "@/components/PersonalizedInsightsCard";
import { useSimulation } from "@/hooks/useSimulation";

const Index = () => {
  const sim = useSimulation(3000);

  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader lastUpdated={sim.lastUpdated} />
      <main className="container px-6 py-6 space-y-6">
        <StatsBar stats={sim.stats} />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <MapPreview />
            <TrafficForecastCard forecastData={sim.forecastData} routes={sim.routes} />
          </div>
          <div className="space-y-6">
            <DeparturePlannerCard departures={sim.departures} />
            <ParkingIntelCard parking={sim.parking} />
          </div>
        </div>
        <PersonalizedInsightsCard />
      </main>
    </div>
  );
};

export default Index;
