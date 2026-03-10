import { GoogleMap, LoadScript, Polyline } from "@react-google-maps/api";
import { Maximize2, Layers, Navigation } from "lucide-react";

const containerStyle = {
  width: "100%",
  height: "400px"
};

const center = {
  lat: 19.0760,
  lng: 72.8777
};

const path = [
  { lat: 19.1136, lng: 72.8697 },
  { lat: 19.0728, lng: 72.8826 }
];

const MapPreview = () => {
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;

  if (!apiKey || apiKey === "your_api_key_here") {
    return (
      <div className="card-glass overflow-hidden animate-slide-up-delay-1 relative group">
        <div className="w-full h-64 lg:h-80 bg-muted flex items-center justify-center">
          <div className="text-center">
            <p className="text-muted-foreground mb-2">Google Maps Integration</p>
            <p className="text-sm text-muted-foreground">
              Please set your VITE_GOOGLE_MAPS_API_KEY in .env file
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card-glass overflow-hidden animate-slide-up-delay-1 relative group">
      <LoadScript googleMapsApiKey={apiKey}>
        <GoogleMap
          mapContainerStyle={containerStyle}
          center={center}
          zoom={12}
        >
          <Polyline
            path={path}
            options={{
              strokeColor: "red",
              strokeWeight: 6
            }}
          />
        </GoogleMap>
      </LoadScript>

      <div className="absolute inset-0 bg-gradient-to-t from-card via-transparent to-transparent pointer-events-none" />
      <div className="absolute top-4 right-4 flex gap-2">
        <button className="p-2 rounded-lg bg-card/80 backdrop-blur border border-border/50 hover:bg-secondary transition-colors">
          <Layers className="w-4 h-4 text-muted-foreground" />
        </button>
        <button className="p-2 rounded-lg bg-card/80 backdrop-blur border border-border/50 hover:bg-secondary transition-colors">
          <Maximize2 className="w-4 h-4 text-muted-foreground" />
        </button>
      </div>
      <div className="absolute bottom-4 left-4 right-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-muted-foreground">Active Route</p>
            <p className="text-sm font-semibold text-foreground">Andheri West → BKC</p>
          </div>
          <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors glow-primary">
            <Navigation className="w-4 h-4" />
            Navigate
          </button>
        </div>
      </div>
    </div>
  );
};

export default MapPreview;
