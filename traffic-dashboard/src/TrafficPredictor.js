import React, { useEffect, useMemo, useState } from "react";

const FEATURE_CONFIG = [
  { key: "vehicle_count", label: "Vehicle Count", min: 0, max: 200, step: 1 },
  { key: "average_speed", label: "Average Speed (km/h)", min: 0, max: 120, step: 0.1 },
  { key: "lane_occupancy", label: "Lane Occupancy", min: 0, max: 1, step: 0.01 },
  { key: "flow_rate", label: "Flow Rate", min: 0, max: 3000, step: 1 },
  { key: "time_of_day", label: "Time of Day (0-23)", min: 0, max: 23, step: 1 },
  { key: "waiting_time", label: "Waiting Time (s)", min: 0, max: 300, step: 0.1 },
  { key: "avg_speed_kmph", label: "Avg Speed KMPH", min: 0, max: 120, step: 0.1 },
  { key: "density_veh_per_km", label: "Density (veh/km)", min: 0, max: 200, step: 0.1 },
  { key: "avg_wait_time_s", label: "Avg Wait Time (s)", min: 0, max: 300, step: 0.1 },
  { key: "occupancy_pct", label: "Occupancy %", min: 0, max: 100, step: 0.1 },
  { key: "flow_veh_per_hr", label: "Flow (veh/hr)", min: 0, max: 4000, step: 1 },
  { key: "queue_length_veh", label: "Queue Length (veh)", min: 0, max: 200, step: 1 },
  { key: "avg_accel_ms2", label: "Avg Accel (m/s²)", min: -2, max: 3, step: 0.01 },
  { key: "SRI", label: "Speed Reduction Index", min: -5, max: 10, step: 0.01 }
];

const BASE_INPUT = {
  vehicle_count: 45,
  average_speed: 35,
  lane_occupancy: 0.5,
  flow_rate: 1000,
  time_of_day: 10,
  waiting_time: 18,
  avg_speed_kmph: 38,
  density_veh_per_km: 32,
  avg_wait_time_s: 22,
  occupancy_pct: 42,
  flow_veh_per_hr: 1350,
  queue_length_veh: 11,
  avg_accel_ms2: 0.6,
  SRI: 1.8
};

const PRESETS = {
  low: {
    vehicle_count: 26,
    average_speed: 54,
    lane_occupancy: 0.28,
    flow_rate: 650,
    time_of_day: 23,
    waiting_time: 6,
    avg_speed_kmph: 58,
    density_veh_per_km: 10,
    avg_wait_time_s: 9,
    occupancy_pct: 18,
    flow_veh_per_hr: 1680,
    queue_length_veh: 2,
    avg_accel_ms2: 0.82,
    SRI: -1.1
  },
  normal: {
    vehicle_count: 58,
    average_speed: 37,
    lane_occupancy: 0.52,
    flow_rate: 980,
    time_of_day: 13,
    waiting_time: 20,
    avg_speed_kmph: 41,
    density_veh_per_km: 31,
    avg_wait_time_s: 24,
    occupancy_pct: 44,
    flow_veh_per_hr: 1450,
    queue_length_veh: 10,
    avg_accel_ms2: 0.5,
    SRI: 1.7
  },
  high: {
    vehicle_count: 82,
    average_speed: 22,
    lane_occupancy: 0.72,
    flow_rate: 1380,
    time_of_day: 18,
    waiting_time: 47,
    avg_speed_kmph: 24,
    density_veh_per_km: 54,
    avg_wait_time_s: 45,
    occupancy_pct: 64,
    flow_veh_per_hr: 980,
    queue_length_veh: 24,
    avg_accel_ms2: -0.12,
    SRI: 3.9
  },
  severe: {
    vehicle_count: 104,
    average_speed: 9,
    lane_occupancy: 0.92,
    flow_rate: 1820,
    time_of_day: 19,
    waiting_time: 115,
    avg_speed_kmph: 12,
    density_veh_per_km: 82,
    avg_wait_time_s: 98,
    occupancy_pct: 88,
    flow_veh_per_hr: 620,
    queue_length_veh: 44,
    avg_accel_ms2: -0.67,
    SRI: 5.6
  }
};

function TrafficPredictor() {
  const [formData, setFormData] = useState(BASE_INPUT);
  const [loading, setLoading] = useState(false);
  const [resetLoading, setResetLoading] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState("");
  const [samples, setSamples] = useState(0);
  const [history, setHistory] = useState([]);
  const [status, setStatus] = useState({ traffic: "unknown", parking: "unknown" });

  const sampleProgress = useMemo(() => Math.min(100, Math.round((samples / 10) * 100)), [samples]);

  useEffect(() => {
    checkServices();
  }, []);

  const checkServices = async () => {
    const result = { traffic: "down", parking: "down" };

    try {
      const response = await fetch("/health");
      if (response.ok) {
        result.traffic = "up";
      }
    } catch (err) {
      result.traffic = "down";
    }

    try {
      const response = await fetch("/parking/health");
      if (response.ok) {
        const data = await response.json();
        result.parking = data.status === "healthy" ? "up" : "degraded";
      }
    } catch (err) {
      result.parking = "down";
    }

    setStatus(result);
  };

  const handleFieldChange = (key, value) => {
    setFormData((prev) => ({
      ...prev,
      [key]: value === "" ? "" : Number(value)
    }));
  };

  const applyPreset = (presetName) => {
    setFormData(PRESETS[presetName]);
    setError("");
  };

  const submitPrediction = async () => {
    setLoading(true);
    setError("");

    try {
      const payload = {};
      for (const field of FEATURE_CONFIG) {
        const val = formData[field.key];
        if (val === "" || Number.isNaN(Number(val))) {
          throw new Error(`Invalid value for ${field.label}`);
        }
        payload[field.key] = Number(val);
      }

      const response = await fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`Prediction API failed with HTTP ${response.status}`);
      }

      const data = await response.json();

      if (data.status === "collecting_data") {
        const collected = Number(data.samples_collected ?? 0);
        setSamples(collected);
        setPrediction({
          type: "collecting",
          title: "Building Sequence Window",
          message: `${collected}/10 samples received`
        });
      } else if (data.status === "success") {
        setSamples(10);
        setPrediction({
          type: "result",
          title: data.congestion_level,
          confidence: Number(data.confidence ?? 0)
        });
      } else {
        throw new Error(data.message || "Unexpected response from API");
      }

      setHistory((prev) => [
        {
          timestamp: new Date().toLocaleTimeString(),
          status: data.status,
          congestion: data.congestion_level || "n/a",
          confidence: Number(data.confidence ?? 0)
        },
        ...prev
      ].slice(0, 8));

      checkServices();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const resetSession = async () => {
    setResetLoading(true);
    setError("");

    try {
      const response = await fetch("/reset", { method: "POST" });
      if (!response.ok) {
        throw new Error(`Reset failed with HTTP ${response.status}`);
      }

      setSamples(0);
      setPrediction({
        type: "idle",
        title: "Buffer Reset",
        message: "Ready for a fresh 10-sample sequence"
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setResetLoading(false);
    }
  };

  const statusLabel = (val) => {
    if (val === "up") return "Operational";
    if (val === "degraded") return "Degraded";
    if (val === "down") return "Unavailable";
    return "Unknown";
  };

  return (
    <main className="dashboard">
      <section className="hero">
        <div>
          <p className="eyebrow">DeepGuardians Platform</p>
          <h1>Traffic + Parking Intelligence Console</h1>
          <p className="hero-text">
            Real-time congestion forecasting with 14-feature inputs, sequence tracking,
            and direct access to parking intelligence workflows in this branch.
          </p>
        </div>
        <div className="hero-actions">
          <button className="ghost-btn" onClick={checkServices}>Refresh Service Status</button>
          <a className="ghost-btn" href="/parking-demo" target="_blank" rel="noreferrer">Open Parking Demo</a>
          <a className="ghost-btn" href="/docs" target="_blank" rel="noreferrer">Open API Docs</a>
        </div>
      </section>

      <section className="status-grid">
        <article className={`status-card ${status.traffic}`}>
          <h3>Traffic API</h3>
          <p>{statusLabel(status.traffic)}</p>
        </article>
        <article className={`status-card ${status.parking}`}>
          <h3>Parking API</h3>
          <p>{statusLabel(status.parking)}</p>
        </article>
        <article className="status-card neutral">
          <h3>Sequence Window</h3>
          <p>{samples}/10 samples</p>
          <div className="progress-track"><div className="progress-bar" style={{ width: `${sampleProgress}%` }} /></div>
        </article>
      </section>

      <section className="workspace-grid">
        <article className="panel">
          <header className="panel-header">
            <h2>Traffic Input Controls</h2>
            <div className="preset-row">
              <button onClick={() => applyPreset("low")}>Low</button>
              <button onClick={() => applyPreset("normal")}>Normal</button>
              <button onClick={() => applyPreset("high")}>High</button>
              <button onClick={() => applyPreset("severe")}>Severe</button>
            </div>
          </header>

          <div className="input-grid">
            {FEATURE_CONFIG.map((field) => (
              <label key={field.key} className="field">
                <span>{field.label}</span>
                <input
                  type="number"
                  value={formData[field.key]}
                  min={field.min}
                  max={field.max}
                  step={field.step}
                  onChange={(event) => handleFieldChange(field.key, event.target.value)}
                />
              </label>
            ))}
          </div>

          <div className="button-row">
            <button className="primary-btn" onClick={submitPrediction} disabled={loading}>
              {loading ? "Predicting..." : "Run Prediction"}
            </button>
            <button className="secondary-btn" onClick={resetSession} disabled={resetLoading}>
              {resetLoading ? "Resetting..." : "Reset Sequence"}
            </button>
          </div>

          {error ? <p className="error-text">{error}</p> : null}
        </article>

        <article className="panel">
          <header className="panel-header">
            <h2>Prediction Output</h2>
          </header>

          <div className="prediction-card">
            {prediction?.type === "result" ? (
              <>
                <p className="prediction-label">Congestion Level</p>
                <h3>{prediction.title}</h3>
                <p className="confidence">Confidence Score: {prediction.confidence.toFixed(3)}</p>
              </>
            ) : prediction ? (
              <>
                <p className="prediction-label">Status</p>
                <h3>{prediction.title}</h3>
                <p>{prediction.message}</p>
              </>
            ) : (
              <>
                <p className="prediction-label">Awaiting Request</p>
                <h3>No prediction yet</h3>
                <p>Submit an input set to start building sequence context.</p>
              </>
            )}
          </div>

          <div className="history">
            <h3>Recent Requests</h3>
            {history.length === 0 ? (
              <p className="muted">No requests submitted in this session.</p>
            ) : (
              <ul>
                {history.map((item, index) => (
                  <li key={`${item.timestamp}-${index}`}>
                    <span>{item.timestamp}</span>
                    <span>{item.status === "success" ? item.congestion : "collecting"}</span>
                    <span>{item.status === "success" ? item.confidence.toFixed(3) : "-"}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </article>
      </section>

      <section className="parking-panel">
        <h2>Parking Intelligence in This Branch</h2>
        <p>
          This branch extends the traffic model with nearby parking search, optimal parking-time suggestions,
          smart departure planning, and user personalization endpoints under <code>/parking/*</code>.
        </p>
        <div className="parking-tags">
          <span>/parking/nearby</span>
          <span>/parking/predict</span>
          <span>/parking/optimal-time</span>
          <span>/parking/smart-departure</span>
          <span>/parking/user/personalized-parking</span>
        </div>
      </section>
    </main>
  );
}

export default TrafficPredictor;
