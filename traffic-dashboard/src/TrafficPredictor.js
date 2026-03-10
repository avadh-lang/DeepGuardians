import React, { useState } from "react";

function TrafficPredictor() {

  const [prediction, setPrediction] = useState("");
  const [loading, setLoading] = useState(false);
  const [samples, setSamples] = useState(0);

  const predictTraffic = async () => {

    const trafficData = {
      vehicle_count: Math.random() * 100 + 20,
      average_speed: Math.random() * 80 + 5,
      lane_occupancy: Math.random(),
      flow_rate: Math.random() * 1500 + 500,
      time_of_day: Math.floor(Math.random() * 24),
      waiting_time: Math.random() * 200,
      avg_speed_kmph: Math.random() * 80 + 5,
      density_veh_per_km: Math.random() * 100,
      avg_wait_time_s: Math.random() * 150,
      occupancy_pct: Math.random() * 100,
      flow_veh_per_hr: Math.random() * 2000 + 500,
      queue_length_veh: Math.random() * 60,
      avg_accel_ms2: Math.random() * 2 - 1,
      SRI: Math.random() * 10 - 2
    };

    setLoading(true);

    try {

      console.log("Sending request with data:", trafficData);

      const response = await fetch("/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(trafficData)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      console.log("Response received:", response);

      const data = await response.json();

      console.log("Data from backend:", data);

      if (data.status === "collecting_data") {
        setPrediction(`Collecting data... ${data.samples_collected}/${data.samples_needed}`);
        setSamples(data.samples_collected);
      } else if (data.status === "success") {
        setPrediction(`🚗 ${data.congestion_level} congestion`);
        setSamples(10);
      } else {
        setPrediction(`Error: ${data.error}`);
      }

    } catch (error) {

      console.error("Fetch error:", error);
      setPrediction(`Error: ${error.message}`);

    } finally {
      setLoading(false);
    }

  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px", fontFamily: "Arial, sans-serif" }}>

      <h1>🚦 AI Traffic Congestion Predictor</h1>

      <p style={{ color: "#666", marginBottom: "20px" }}>
        Requires 10+ consecutive predictions to analyze traffic patterns
      </p>

      <div style={{ marginBottom: "20px" }}>
        <button 
          onClick={predictTraffic}
          disabled={loading}
          style={{
            padding: "12px 30px",
            fontSize: "16px",
            backgroundColor: loading ? "#ccc" : "#007bff",
            color: "white",
            border: "none",
            borderRadius: "5px",
            cursor: loading ? "not-allowed" : "pointer"
          }}
        >
          {loading ? "Predicting..." : "Predict Traffic"}
        </button>
      </div>

      <div style={{
        padding: "20px",
        backgroundColor: "#f0f0f0",
        borderRadius: "5px",
        minHeight: "60px",
        display: "flex",
        alignItems: "center",
        justifyContent: "center"
      }}>
        <div>
          <h2 style={{ margin: "0 0 10px 0" }}>{prediction || "Click to predict"}</h2>
          <p style={{ margin: "0", color: "#666", fontSize: "14px" }}>
            Samples collected: {samples}/10
          </p>
        </div>
      </div>

    </div>
  );
}

export default TrafficPredictor;