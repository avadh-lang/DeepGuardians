import { useState, useEffect, useCallback, useRef } from "react";

const clamp = (v: number, min: number, max: number) => Math.max(min, Math.min(max, v));
const jitter = (base: number, range: number) => base + (Math.random() - 0.5) * 2 * range;

export interface TrafficDataPoint {
  time: string;
  congestion: number;
  predicted: number;
}

export interface RouteStatus {
  name: string;
  status: "heavy" | "moderate" | "light";
  change: number;
  eta: string;
}

export interface DepartureSuggestion {
  time: string;
  duration: string;
  savings: string;
  route: string;
  confidence: number;
  optimal: boolean;
}

export interface ParkingSpot {
  name: string;
  available: number;
  total: number;
  price: string;
  trend: "filling" | "stable" | "critical";
  distance: string;
  eta: string;
}

export interface StatsData {
  avgCommute: number;
  routesAnalyzed: number;
  parkingFound: number;
  aiAccuracy: number;
}

export interface SimulationState {
  forecastData: TrafficDataPoint[];
  routes: RouteStatus[];
  departures: DepartureSuggestion[];
  parking: ParkingSpot[];
  stats: StatsData;
  lastUpdated: Date;
}

const baseForecast: TrafficDataPoint[] = [
  { time: "6AM", congestion: 20, predicted: 22 },
  { time: "7AM", congestion: 45, predicted: 48 },
  { time: "8AM", congestion: 82, predicted: 78 },
  { time: "9AM", congestion: 90, predicted: 85 },
  { time: "10AM", congestion: 65, predicted: 60 },
  { time: "11AM", congestion: 40, predicted: 42 },
  { time: "12PM", congestion: 35, predicted: 38 },
  { time: "1PM", congestion: 50, predicted: 52 },
  { time: "2PM", congestion: 55, predicted: 50 },
  { time: "3PM", congestion: 60, predicted: 58 },
  { time: "4PM", congestion: 75, predicted: 72 },
  { time: "5PM", congestion: 88, predicted: 90 },
  { time: "6PM", congestion: 92, predicted: 88 },
  { time: "7PM", congestion: 70, predicted: 65 },
  { time: "8PM", congestion: 45, predicted: 42 },
];

const baseParking = [
  { name: "BKC Parking Complex", available: 23, total: 120, price: "₹60/hr", trend: "filling" as const, distance: "0.3 km", eta: "2 min" },
  { name: "Jio World Centre P2", available: 8, total: 80, price: "₹80/hr", trend: "filling" as const, distance: "0.8 km", eta: "5 min" },
  { name: "MMRDA Grounds Lot", available: 45, total: 200, price: "₹40/hr", trend: "stable" as const, distance: "1.2 km", eta: "8 min" },
  { name: "Trade Centre Basement", available: 3, total: 50, price: "₹100/hr", trend: "critical" as const, distance: "0.1 km", eta: "1 min" },
];

function getStatus(congestion: number): "heavy" | "moderate" | "light" {
  if (congestion > 70) return "heavy";
  if (congestion > 40) return "moderate";
  return "light";
}

function etaFromCongestion(base: number, congestion: number): string {
  const mins = Math.round(base * (0.5 + congestion / 100));
  return `${mins} min`;
}

export function useSimulation(intervalMs = 3000) {
  const tickRef = useRef(0);

  const generateState = useCallback((): SimulationState => {
    const tick = tickRef.current++;

    // Forecast: smoothly jitter congestion values
    const forecastData = baseForecast.map((d) => ({
      time: d.time,
      congestion: clamp(Math.round(jitter(d.congestion, 8)), 5, 100),
      predicted: clamp(Math.round(jitter(d.predicted, 6)), 5, 100),
    }));

    // Routes: derive from forecast peaks
    const weCongestion = clamp(Math.round(jitter(78, 12)), 20, 100);
    const eeCongestion = clamp(Math.round(jitter(55, 10)), 20, 100);
    const sclrCongestion = clamp(Math.round(jitter(30, 8)), 10, 80);

    const routes: RouteStatus[] = [
      { name: "Western Express Hwy", status: getStatus(weCongestion), change: Math.round(jitter(0, 15)), eta: etaFromCongestion(45, weCongestion) },
      { name: "Eastern Express Hwy", status: getStatus(eeCongestion), change: Math.round(jitter(0, 10)), eta: etaFromCongestion(38, eeCongestion) },
      { name: "SCLR", status: getStatus(sclrCongestion), change: Math.round(jitter(0, 8)), eta: etaFromCongestion(25, sclrCongestion) },
    ];

    // Departures: fluctuate durations and confidence
    const baseDurations = [32, 41, 50];
    const durations = baseDurations.map((d) => clamp(Math.round(jitter(d, 5)), 18, 65));
    const minDur = Math.min(...durations);
    const departures: DepartureSuggestion[] = [
      { time: "7:15 AM", duration: `${durations[0]} min`, savings: `${Math.max(0, durations[2] - durations[0])} min`, route: "SCLR → BKC Connector", confidence: clamp(Math.round(jitter(94, 4)), 75, 99), optimal: durations[0] === minDur },
      { time: "7:45 AM", duration: `${durations[1]} min`, savings: `${Math.max(0, durations[2] - durations[1])} min`, route: "Western Express Hwy", confidence: clamp(Math.round(jitter(87, 5)), 70, 99), optimal: durations[1] === minDur },
      { time: "8:30 AM", duration: `${durations[2]} min`, savings: "0 min", route: "Eastern Express Hwy", confidence: clamp(Math.round(jitter(78, 5)), 65, 95), optimal: durations[2] === minDur },
    ];

    // Parking: decrement/increment available spots
    const parking: ParkingSpot[] = baseParking.map((p) => {
      const delta = Math.round((Math.random() - 0.4) * 4); // slight bias toward filling
      const available = clamp(p.available - delta * (tick % 5 === 0 ? 2 : 1), 0, p.total);
      const ratio = available / p.total;
      const trend = ratio < 0.08 ? "critical" as const : ratio < 0.25 ? "filling" as const : "stable" as const;
      return { ...p, available, trend };
    });

    // Stats
    const stats: StatsData = {
      avgCommute: clamp(Math.round(jitter(34, 3)), 25, 50),
      routesAnalyzed: 2847 + tick * Math.round(jitter(12, 5)),
      parkingFound: clamp(parseFloat(jitter(98.2, 1.5).toFixed(1)), 90, 99.9),
      aiAccuracy: clamp(parseFloat(jitter(94.7, 1).toFixed(1)), 88, 99.5),
    };

    return { forecastData, routes, departures, parking, stats, lastUpdated: new Date() };
  }, []);

  const [state, setState] = useState<SimulationState>(generateState);

  useEffect(() => {
    const id = setInterval(() => setState(generateState()), intervalMs);
    return () => clearInterval(id);
  }, [generateState, intervalMs]);

  return state;
}
