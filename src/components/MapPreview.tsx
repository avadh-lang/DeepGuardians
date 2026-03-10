import { useState, useRef, useEffect } from "react";
import { GoogleMap, LoadScript, DirectionsRenderer, Autocomplete } from "@react-google-maps/api";
import { Maximize2, Layers, Navigation } from "lucide-react";

const containerStyle = {
  width: "100%",
  height: "400px"
};

const center = {
  lat: 19.0760,
  lng: 72.8777
};

const libraries = ["places", "directions"];

const MapPreview = () => {
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
  const [map, setMap] = useState(null);
  const [directionsResult, setDirectionsResult] = useState(null);
  const [origin, setOrigin] = useState("Andheri West, Mumbai");
  const [destination, setDestination] = useState("Bandra Kurla Complex, Mumbai");
  const autocompleteRef = useRef(null);
  const directionsServiceRef = useRef(null);

  useEffect(() => {
    if (map && directionsServiceRef.current && origin && destination) {
      directionsServiceRef.current.route(
        {
          origin: origin,
          destination: destination,
          travelMode: window.google?.maps?.TravelMode?.DRIVING
        },
        (result, status) => {
          if (status === window.google?.maps?.DirectionsStatus?.OK) {
            setDirectionsResult(result);
          } else {
            console.error("Directions request failed:", status);
          }
        }
      );
    }
  }, [map, origin, destination]);

  const handleMapLoad = (mapInstance) => {
    setMap(mapInstance);
    directionsServiceRef.current = new window.google.maps.DirectionsService();
  };

  const handlePlaceChanged = () => {
    if (autocompleteRef.current) {
      const place = autocompleteRef.current.getPlace();
      if (place && place.geometry) {
        setDestination(place.formatted_address || place.name);
        console.log("Selected place:", place);
      }
    }
  };

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
      <div className="absolute top-4 left-4 right-16 z-10">
        <LoadScript googleMapsApiKey={apiKey} libraries={libraries}>
          <Autocomplete
            onLoad={(autocomplete) => {
              autocompleteRef.current = autocomplete;
            }}
            onPlaceChanged={handlePlaceChanged}
          >
            <input
              type="text"
              placeholder="Search destination..."
              className="w-full px-4 py-2 rounded-lg bg-card/90 backdrop-blur border border-border/50 text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              defaultValue={destination}
            />
          </Autocomplete>
        </LoadScript>
      </div>

      <LoadScript googleMapsApiKey={apiKey} libraries={libraries}>
        <GoogleMap
          mapContainerStyle={containerStyle}
          center={center}
          zoom={12}
          onLoad={handleMapLoad}
        >
          {directionsResult && (
            <DirectionsRenderer
              directions={directionsResult}
              options={{
                polylineOptions: {
                  strokeColor: "#EF4444",
                  strokeWeight: 6,
                  strokeOpacity: 0.8
                },
                suppressMarkers: false
              }}
            />
          )}
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
            <p className="text-sm font-semibold text-foreground">
              {directionsResult?.routes[0]?.summary || "Andheri West → BKC"}
            </p>
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
