import { GoogleMap, LoadScript, DirectionsRenderer } from "@react-google-maps/api";
import { useEffect, useState } from "react";

const containerStyle = {
  width: "100%",
  height: "400px"
};

const center = { lat: 19.0760, lng: 72.8777 };

function TrafficMap({ route }) {
  const [directions, setDirections] = useState(null);

  useEffect(() => {
    if (!route) return;

    const directionsService = new window.google.maps.DirectionsService();

    directionsService.route(
      {
        origin: route.origin,
        destination: route.destination,
        travelMode: window.google.maps.TravelMode.DRIVING
      },
      (result, status) => {
        console.log("Directions status:", status);

        if (status === "OK") {
          setDirections(result);
        }
      }
    );
  }, [route]);

  return (
    <LoadScript googleMapsApiKey={import.meta.env.VITE_GOOGLE_MAPS_API_KEY}>
      <GoogleMap mapContainerStyle={containerStyle} center={center} zoom={12}>
        {directions && <DirectionsRenderer directions={directions} />}
      </GoogleMap>
    </LoadScript>
  );
}

export default TrafficMap;