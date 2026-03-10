import { GoogleMap, LoadScript, Marker, TrafficLayer } from "@react-google-maps/api";

const containerStyle = {
  width: "100%",
  height: "400px"
};

const center = {
  lat: 19.1136, // Andheri West
  lng: 72.8697
};

const congestionPoints = [
  { lat: 19.0728, lng: 72.8826 }, // BKC
  { lat: 19.0920, lng: 72.8700 }
];

function TrafficMap() {
  return (
    <LoadScript googleMapsApiKey="YOUR_API_KEY">
      <GoogleMap mapContainerStyle={containerStyle} center={center} zoom={12}>
        
        {/* Live Traffic Layer */}
        <TrafficLayer autoUpdate />

        {/* Congestion markers */}
        {congestionPoints.map((point, index) => (
          <Marker key={index} position={point} />
        ))}

      </GoogleMap>
    </LoadScript>
  );
}

export default TrafficMap;