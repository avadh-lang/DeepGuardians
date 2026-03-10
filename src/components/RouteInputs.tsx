import { useState } from "react";

function RouteInputs({ setRoute }) {

  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!from || !to) {
      alert("Please enter both locations");
      return;
    }

    setRoute({
      origin: from,
      destination: to
    });
  };

  return (
    <div style={{ padding: "15px" }}>

      <form onSubmit={handleSubmit} style={{ display: "flex", gap: "10px" }}>

        <input
          type="text"
          placeholder="From (Origin)"
          value={from}
          onChange={(e) => setFrom(e.target.value)}
          style={{
            padding: "10px",
            width: "220px",
            borderRadius: "8px",
            border: "1px solid #ccc"
          }}
        />

        <input
          type="text"
          placeholder="To (Destination)"
          value={to}
          onChange={(e) => setTo(e.target.value)}
          style={{
            padding: "10px",
            width: "220px",
            borderRadius: "8px",
            border: "1px solid #ccc"
          }}
        />

        <button
          type="submit"
          style={{
            padding: "10px 20px",
            backgroundColor: "#3b82f6",
            color: "white",
            borderRadius: "8px",
            border: "none",
            cursor: "pointer"
          }}
        >
          Find Route
        </button>

      </form>

    </div>
  );
}

export default RouteInputs;