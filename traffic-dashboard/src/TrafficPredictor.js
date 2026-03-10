import React, { useState } from "react";

function TrafficPredictor() {

  const [prediction, setPrediction] = useState("");

  const predictTraffic = async () => {

    const trafficData = {
      vehicle_count: 50,
      average_speed: 35,
      lane_occupancy: 0.6,
      flow_rate: 80,
      waiting_time: 20,
      density_veh_per_km: 30,
      queue_length_veh: 10,
      avg_accel_ms2: 1.2
    };

    try {

      console.log("Sending request...");

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

      setPrediction(data.congestion_level);

    } catch (error) {

      console.error("Fetch error:", error);
      setPrediction(`Error: ${error.message}`);

    }

  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>

      <h1>AI Traffic Congestion Predictor</h1>

      <button onClick={predictTraffic}>
        Predict Traffic
      </button>

      <h2>{prediction}</h2>

    </div>
  );
}

export default TrafficPredictor;