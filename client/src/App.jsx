import { useEffect, useMemo, useRef, useState } from "react";
import { DirectionsRenderer, GoogleMap, Marker, Polyline, useJsApiLoader } from "@react-google-maps/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || "";

function buildDefaultDeparture() {
  const next = new Date();
  next.setMinutes(next.getMinutes() + 30);
  const timezoneOffset = next.getTimezoneOffset() * 60000;
  return new Date(next - timezoneOffset).toISOString().slice(0, 16);
}

function formatDuration(minutes) {
  if (!minutes && minutes !== 0) return "N/A";
  const hrs = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (!hrs) return `${mins} min`;
  return `${hrs} hr ${mins} min`;
}

function levelTone(level) {
  if (level === "Severe") return "tone-danger";
  if (level === "Heavy") return "tone-warning";
  if (level === "Moderate") return "tone-caution";
  return "tone-safe";
}

function RouteMap({ analysis }) {
  const mapRef = useRef(null);
  const [directions, setDirections] = useState(null);
  const [routeError, setRouteError] = useState("");
  const [routeReady, setRouteReady] = useState(false);

  const fallbackPath = useMemo(() => {
    if (!analysis) return [];
    return [
      { lat: analysis.trip.origin.lat, lng: analysis.trip.origin.lng },
      { lat: analysis.trip.destination.lat, lng: analysis.trip.destination.lng },
    ];
  }, [analysis]);

  useEffect(() => {
    if (!analysis || !window.google?.maps) return;

    setRouteError("");
    setDirections(null);
    setRouteReady(false);

    const service = new window.google.maps.DirectionsService();
    service.route(
      {
        origin: analysis.trip.origin.label,
        destination: analysis.trip.destination.label,
        travelMode: window.google.maps.TravelMode.DRIVING,
        provideRouteAlternatives: false,
      },
      (result, status) => {
        if (status === "OK" && result) {
          setDirections(result);
          setRouteReady(true);
          return;
        }

        setRouteError(`Google Directions could not build this route (${status}).`);
      }
    );
  }, [analysis]);

  useEffect(() => {
    if (!mapRef.current || !window.google?.maps || fallbackPath.length !== 2) return;

    const bounds = new window.google.maps.LatLngBounds();
    fallbackPath.forEach((point) => bounds.extend(point));
    mapRef.current.fitBounds(bounds, 80);
  }, [fallbackPath, directions]);

  const iframeDirectionsUrl = analysis
    ? `https://www.google.com/maps/embed/v1/directions?key=${encodeURIComponent(
        GOOGLE_MAPS_API_KEY
      )}&origin=${encodeURIComponent(analysis.trip.origin.label)}&destination=${encodeURIComponent(
        analysis.trip.destination.label
      )}&mode=driving`
    : "";

  return (
    <>
      {!routeError ? (
        <GoogleMap
          mapContainerClassName="traffic-map"
          center={{ lat: 19.076, lng: 72.8777 }}
          zoom={11}
          onLoad={(map) => {
            mapRef.current = map;
          }}
          options={{
            disableDefaultUI: true,
            zoomControl: true,
            streetViewControl: false,
            mapTypeControl: false,
            fullscreenControl: false,
            styles: [
              { elementType: "geometry", stylers: [{ color: "#122033" }] },
              { elementType: "labels.text.fill", stylers: [{ color: "#dce7f8" }] },
              { elementType: "labels.text.stroke", stylers: [{ color: "#122033" }] },
              { featureType: "road", elementType: "geometry", stylers: [{ color: "#22344c" }] },
              { featureType: "water", elementType: "geometry", stylers: [{ color: "#0b3a56" }] },
            ],
          }}
        >
          {analysis ? (
            <>
              <Marker position={analysis.trip.origin} label="A" />
              <Marker position={analysis.trip.destination} label="B" />
              {directions ? (
                <DirectionsRenderer
                  directions={directions}
                  options={{
                    suppressMarkers: true,
                    polylineOptions: {
                      strokeColor: "#ff8750",
                      strokeOpacity: 0.95,
                      strokeWeight: 5,
                    },
                  }}
                />
              ) : null}
              {!routeReady && fallbackPath.length === 2 ? (
                <Polyline
                  path={fallbackPath}
                  options={{
                    strokeColor: "#79b8ff",
                    strokeOpacity: 0.85,
                    strokeWeight: 4,
                    icons: [
                      {
                        icon: {
                          path: "M 0,-1 0,1",
                          strokeOpacity: 1,
                          strokeColor: "#79b8ff",
                          scale: 4,
                        },
                        offset: "0",
                        repeat: "18px",
                      },
                    ],
                  }}
                />
              ) : null}
            </>
          ) : null}
        </GoogleMap>
      ) : (
        <iframe
          title="Google Maps Directions"
          className="traffic-map-frame"
          src={iframeDirectionsUrl}
          loading="lazy"
          referrerPolicy="no-referrer-when-downgrade"
        />
      )}
      <p className="map-caption">
        The route view now always connects your From and To points: first with Google driving directions, and if that fails, with a direct traced line between the two locations.
      </p>
      {routeError ? <p className="error-copy route-error-copy">{routeError}</p> : null}
    </>
  );
}

export default function App() {
  const [form, setForm] = useState({
    origin: "Andheri East, Mumbai",
    destination: "Bandra Kurla Complex, Mumbai",
    departure_time: buildDefaultDeparture(),
    parking_needed: true,
    commute_style: "balanced",
  });
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const { isLoaded, loadError } = useJsApiLoader({
    googleMapsApiKey: GOOGLE_MAPS_API_KEY,
    libraries: ["geometry"],
  });

  async function runAnalysis(event) {
    if (event) event.preventDefault();

    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/api/traffic/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...form,
          departure_time: new Date(form.departure_time).toISOString(),
        }),
      });

      if (!response.ok) {
        throw new Error("Unable to analyze this trip right now.");
      }

      const result = await response.json();
      setAnalysis(result);
    } catch (requestError) {
      setError(requestError.message || "Unable to load traffic insights.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    runAnalysis();
  }, []);

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  const currentLevel = analysis?.route?.congestion_level || "Moderate";
  const mapStatusMessage = !GOOGLE_MAPS_API_KEY
    ? "Google Maps key is missing. Add VITE_GOOGLE_MAPS_API_KEY and restart the frontend."
    : loadError
      ? "Google Maps failed to load. This is usually an API key, billing, or referrer restriction issue."
      : null;

  return (
    <div className="app-shell">
      <section className="hero-panel">
        <div className="hero-copy">
          <span className="eyebrow">UrbanFlow AI</span>
          <h1>Predict congestion before the commute starts.</h1>
          <p>
            Plan a Mumbai trip from <strong>From</strong> to <strong>To</strong>, forecast traffic intensity,
            compare departure windows, and get a parking signal before you leave.
          </p>
        </div>

        <div className="hero-metrics">
          <div className="metric-card standout">
            <span>Forecasted Traffic</span>
            <strong className={levelTone(currentLevel)}>{analysis?.route?.congestion_level || "Loading"}</strong>
            <p>{analysis?.route?.forecast_basis || "Preparing your first route forecast."}</p>
          </div>
          <div className="metric-card">
            <span>Predicted Trip Time</span>
            <strong>{formatDuration(analysis?.route?.predicted_duration_minutes)}</strong>
            <p>Includes congestion pressure for your selected departure.</p>
          </div>
          <div className="metric-card">
            <span>Potential Time Saved</span>
            <strong>{analysis?.advice?.time_saved_minutes ?? 0} min</strong>
            <p>Compared with the best nearby departure window.</p>
          </div>
        </div>
      </section>

      <section className="workspace-grid">
        <div className="planner-card glass-card">
          <div className="section-heading">
            <span className="section-kicker">Trip Planner</span>
            <h2>From -&gt; To commuter planning</h2>
          </div>

          <form className="planner-form" onSubmit={runAnalysis}>
            <label>
              From
              <input
                type="text"
                value={form.origin}
                onChange={(event) => updateField("origin", event.target.value)}
                placeholder="Powai, Mumbai"
                required
              />
            </label>

            <label>
              To
              <input
                type="text"
                value={form.destination}
                onChange={(event) => updateField("destination", event.target.value)}
                placeholder="BKC, Mumbai"
                required
              />
            </label>

            <div className="inline-grid">
              <label>
                Departure
                <input
                  type="datetime-local"
                  value={form.departure_time}
                  onChange={(event) => updateField("departure_time", event.target.value)}
                  required
                />
              </label>

              <label>
                Priority
                <select
                  value={form.commute_style}
                  onChange={(event) => updateField("commute_style", event.target.value)}
                >
                  <option value="balanced">Balanced</option>
                  <option value="fastest">Fastest arrival</option>
                  <option value="lowest_stress">Lowest stress</option>
                </select>
              </label>
            </div>

            <label className="toggle-row">
              <input
                type="checkbox"
                checked={form.parking_needed}
                onChange={(event) => updateField("parking_needed", event.target.checked)}
              />
              <span>Include parking availability estimate</span>
            </label>

            <button type="submit" className="primary-button" disabled={loading}>
              {loading ? "Analyzing traffic..." : "Analyze commute"}
            </button>

            {error ? <p className="error-copy">{error}</p> : null}
          </form>

          <div className="insight-strip">
            <div>
              <span>Data source</span>
              <strong>{analysis?.route?.data_source === "google_maps" ? "Live maps + forecast" : "Forecast heuristic"}</strong>
            </div>
            <div>
              <span>Distance</span>
              <strong>{analysis?.route?.distance_km ? `${analysis.route.distance_km} km` : "N/A"}</strong>
            </div>
            <div>
              <span>Stress index</span>
              <strong>{analysis?.advice?.stress_index ?? "N/A"}</strong>
            </div>
          </div>
        </div>

        <div className="map-card glass-card">
          <div className="section-heading">
            <span className="section-kicker">Route View</span>
            <h2>Forecasted corridor snapshot</h2>
          </div>

          {mapStatusMessage ? (
            <div className="map-error-panel">
              <strong>Map unavailable</strong>
              <p>{mapStatusMessage}</p>
              <p className="map-error-hint">
                Check that the key is valid, billing is enabled, and `Maps JavaScript API` is allowed for your current origin.
              </p>
            </div>
          ) : !isLoaded ? (
            <div className="map-loading-panel">
              <strong>Loading Google Maps...</strong>
              <p>The route view will appear as soon as the Maps SDK is ready.</p>
            </div>
          ) : (
            <RouteMap analysis={analysis} />
          )}
        </div>
      </section>

      <section className="results-grid">
        <article className="glass-card summary-card">
          <div className="section-heading">
            <span className="section-kicker">Departure Advice</span>
            <h2>{analysis?.advice?.headline || "Choose a trip to get timing advice."}</h2>
          </div>
          <div className="summary-metrics">
            <div>
              <span>Current estimate</span>
              <strong>{formatDuration(analysis?.route?.predicted_duration_minutes)}</strong>
            </div>
            <div>
              <span>Live traffic time</span>
              <strong>{formatDuration(analysis?.route?.current_duration_minutes)}</strong>
            </div>
            <div>
              <span>Delay vs free flow</span>
              <strong>{formatDuration(analysis?.route?.delay_minutes)}</strong>
            </div>
          </div>
        </article>

        <article className="glass-card windows-card">
          <div className="section-heading">
            <span className="section-kicker">Best Windows</span>
            <h2>Nearby departure options</h2>
          </div>
          <div className="window-list">
            {(analysis?.forecast_windows || []).map((option) => (
              <div key={option.departure_time} className="window-row">
                <div>
                  <strong>{option.label}</strong>
                  <span>{option.offset_minutes === 0 ? "Selected slot" : `${option.offset_minutes > 0 ? "+" : ""}${option.offset_minutes} min`}</span>
                </div>
                <div>
                  <strong>{formatDuration(option.predicted_duration_minutes)}</strong>
                  <span className={levelTone(option.congestion_level)}>{option.congestion_level}</span>
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="glass-card parking-card">
          <div className="section-heading">
            <span className="section-kicker">Parking Intelligence</span>
            <h2>{analysis?.parking?.availability || "Waiting for trip analysis"}</h2>
          </div>
          <div className="parking-score">
            <strong>{analysis?.parking?.score ?? "--"}</strong>
            <span>/ 100</span>
          </div>
          <p>{analysis?.parking?.guidance || "Parking guidance will appear here if enabled."}</p>
        </article>
      </section>
    </div>
  );
}
