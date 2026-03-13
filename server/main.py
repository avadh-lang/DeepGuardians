from __future__ import annotations

import math
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Literal

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    import googlemaps
except ModuleNotFoundError:  # pragma: no cover - fallback for environments without installed deps
    googlemaps = None


ROOT_ENV = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ROOT_ENV)

app = FastAPI(
    title="UrbanFlow Traffic API",
    description="Predictive urban traffic intelligence and departure planning for metro commuters.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


MUMBAI_COORDINATES = {
    "bandra": (19.0596, 72.8295),
    "andheri": (19.1136, 72.8697),
    "powai": (19.1197, 72.9050),
    "thane": (19.2183, 72.9781),
    "kurla": (19.0728, 72.8826),
    "colaba": (18.9067, 72.8147),
    "dadar": (19.0178, 72.8478),
    "lower parel": (18.9988, 72.8258),
    "bkc": (19.0679, 72.8696),
    "worli": (19.0176, 72.8174),
    "goregaon": (19.1648, 72.8496),
    "mumbai": (19.0760, 72.8777),
    "navi mumbai": (19.0330, 73.0297),
}


class LocationPayload(BaseModel):
    label: str
    lat: float
    lng: float


class TripAnalysisRequest(BaseModel):
    origin: str = Field(..., min_length=2, description="Starting point")
    destination: str = Field(..., min_length=2, description="Destination")
    departure_time: datetime = Field(..., description="Requested departure time")
    parking_needed: bool = True
    commute_style: Literal["balanced", "fastest", "lowest_stress"] = "balanced"


class HealthResponse(BaseModel):
    status: str
    maps_configured: bool


def maps_api_key() -> str | None:
    return os.getenv("GOOGLE_MAPS_API_KEY") or os.getenv("VITE_GOOGLE_MAPS_API_KEY")


def get_maps_client() -> Any | None:
    key = maps_api_key()
    if not key or googlemaps is None:
        return None

    try:
        return googlemaps.Client(key=key)
    except Exception:
        return None


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def round_coord(value: float) -> float:
    return round(value, 6)


def location_bias_multiplier(text: str) -> float:
    normalized = text.lower()
    multipliers = {
        "bkc": 1.15,
        "kurla": 1.12,
        "andheri": 1.1,
        "powai": 1.08,
        "thane": 1.08,
        "worli": 1.12,
        "lower parel": 1.13,
        "airport": 1.14,
        "station": 1.1,
        "mall": 1.08,
    }
    factor = 1.0
    for keyword, multiplier in multipliers.items():
        if keyword in normalized:
            factor = max(factor, multiplier)
    return factor


def congestion_profile(departure_time: datetime) -> tuple[int, str]:
    weekday = departure_time.weekday()
    hour = departure_time.hour + departure_time.minute / 60

    if weekday < 5:
        if 7 <= hour < 11:
            return 82, "Morning commute surge"
        if 11 <= hour < 16:
            return 58, "Midday mixed traffic"
        if 16 <= hour < 21:
            return 88, "Evening peak congestion"
        if 21 <= hour < 23:
            return 42, "Late evening easing"
        return 24, "Off-peak window"

    if 10 <= hour < 14:
        return 54, "Weekend shopping rush"
    if 17 <= hour < 22:
        return 62, "Weekend leisure traffic"
    return 28, "Relatively free-flowing"


def congestion_level(score: float) -> str:
    if score >= 80:
        return "Severe"
    if score >= 60:
        return "Heavy"
    if score >= 40:
        return "Moderate"
    return "Light"


def parking_profile(destination: str, departure_time: datetime) -> tuple[int, str, str]:
    base = 68
    area_text = destination.lower()

    if any(term in area_text for term in ["bkc", "lower parel", "worli", "andheri", "kurla"]):
        base -= 18
    if any(term in area_text for term in ["mall", "station", "market", "hospital"]):
        base -= 10
    if departure_time.hour in {9, 10, 18, 19, 20}:
        base -= 14
    if departure_time.weekday() >= 5 and 12 <= departure_time.hour <= 21:
        base -= 10

    score = int(clamp(base, 12, 90))
    if score >= 70:
        label = "High"
        guidance = "Street and structured parking should be reasonably available."
    elif score >= 45:
        label = "Medium"
        guidance = "Expect some search time; covered parking is safer than on-street spots."
    else:
        label = "Low"
        guidance = "Parking pressure is likely high. Reserve in advance or switch to park-and-ride."
    return score, label, guidance


def haversine_km(start: tuple[float, float], end: tuple[float, float]) -> float:
    lat1, lon1 = map(math.radians, start)
    lat2, lon2 = map(math.radians, end)

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(a))


def fallback_location(query: str) -> LocationPayload:
    normalized = query.lower()
    for key, coords in MUMBAI_COORDINATES.items():
        if key in normalized:
            return LocationPayload(label=query.title(), lat=coords[0], lng=coords[1])
    return LocationPayload(label=query.title(), lat=19.0760, lng=72.8777)


def geocode_with_fallback(client: Any | None, query: str) -> LocationPayload:
    if client:
        try:
            results = client.geocode(query, region="in")
            if results:
                top_result = results[0]
                location = top_result["geometry"]["location"]
                return LocationPayload(
                    label=top_result.get("formatted_address", query),
                    lat=round_coord(location["lat"]),
                    lng=round_coord(location["lng"]),
                )
        except Exception:
            pass
    return fallback_location(query)


def live_route_snapshot(
    client: Any | None,
    origin: LocationPayload,
    destination: LocationPayload,
    departure_time: datetime,
) -> dict[str, Any]:
    if client:
        try:
            directions = client.directions(
                (origin.lat, origin.lng),
                (destination.lat, destination.lng),
                mode="driving",
                departure_time=departure_time,
                alternatives=False,
            )
            if directions:
                route = directions[0]
                leg = route["legs"][0]
                live_seconds = leg.get("duration_in_traffic", leg["duration"])["value"]
                freeflow_seconds = leg["duration"]["value"]
                return {
                    "distance_km": round(leg["distance"]["value"] / 1000, 1),
                    "freeflow_minutes": round(freeflow_seconds / 60),
                    "live_minutes": round(live_seconds / 60),
                    "polyline": route.get("overview_polyline", {}).get("points"),
                    "path": [
                        {
                            "lat": round_coord(origin.lat),
                            "lng": round_coord(origin.lng),
                        },
                        {
                            "lat": round_coord(destination.lat),
                            "lng": round_coord(destination.lng),
                        },
                    ],
                    "source": "google_maps",
                }
        except Exception:
            pass

    air_distance = haversine_km((origin.lat, origin.lng), (destination.lat, destination.lng))
    road_distance = max(air_distance * 1.33, 3.5)
    freeflow_minutes = round((road_distance / 32) * 60)
    return {
        "distance_km": round(road_distance, 1),
        "freeflow_minutes": max(freeflow_minutes, 12),
        "live_minutes": max(freeflow_minutes, 12),
        "polyline": None,
        "path": [
            {"lat": round_coord(origin.lat), "lng": round_coord(origin.lng)},
            {"lat": round_coord(destination.lat), "lng": round_coord(destination.lng)},
        ],
        "source": "heuristic",
    }


def predicted_trip_metrics(
    request: TripAnalysisRequest,
    distance_km: float,
    freeflow_minutes: int,
    live_minutes: int,
) -> dict[str, Any]:
    base_score, profile_label = congestion_profile(request.departure_time)
    live_ratio = live_minutes / max(freeflow_minutes, 1)
    distance_penalty = min(distance_km * 1.4, 16)
    corridor_factor = location_bias_multiplier(request.origin) * location_bias_multiplier(request.destination)
    style_modifier = {
        "fastest": 4,
        "balanced": 0,
        "lowest_stress": -6,
    }[request.commute_style]

    score = base_score + (live_ratio - 1) * 42 + distance_penalty + style_modifier
    score = clamp(score * corridor_factor, 8, 97)
    congestion = congestion_level(score)

    predicted_ratio = 1 + (score / 100) * 0.8
    predicted_minutes = round(max(freeflow_minutes * predicted_ratio, live_minutes * 0.92))
    delay_minutes = max(predicted_minutes - freeflow_minutes, 0)

    return {
        "congestion_score": round(score, 1),
        "congestion_level": congestion,
        "profile_label": profile_label,
        "predicted_minutes": predicted_minutes,
        "delay_minutes": delay_minutes,
        "live_ratio": round(live_ratio, 2),
    }


def build_departure_windows(
    request: TripAnalysisRequest,
    distance_km: float,
    freeflow_minutes: int,
    live_minutes: int,
) -> list[dict[str, Any]]:
    options = []
    for offset in (-60, -30, 0, 30, 60, 90):
        candidate_time = request.departure_time + timedelta(minutes=offset)
        metrics = predicted_trip_metrics(request.model_copy(update={"departure_time": candidate_time}), distance_km, freeflow_minutes, live_minutes)
        options.append(
            {
                "label": candidate_time.strftime("%I:%M %p").lstrip("0"),
                "departure_time": candidate_time.isoformat(),
                "offset_minutes": offset,
                "congestion_level": metrics["congestion_level"],
                "congestion_score": metrics["congestion_score"],
                "predicted_duration_minutes": metrics["predicted_minutes"],
            }
        )

    return sorted(options, key=lambda item: item["predicted_duration_minutes"])


def recommendation_summary(best_option: dict[str, Any], selected_metrics: dict[str, Any]) -> tuple[str, int]:
    time_saved = max(selected_metrics["predicted_minutes"] - best_option["predicted_duration_minutes"], 0)
    if best_option["offset_minutes"] < 0:
        summary = f"Leaving {abs(best_option['offset_minutes'])} minutes earlier should reduce delay pressure."
    elif best_option["offset_minutes"] > 0:
        summary = f"Delaying departure by {best_option['offset_minutes']} minutes should avoid the worst congestion band."
    else:
        summary = "Your selected departure is already close to the best available window."
    return summary, time_saved


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", maps_configured=bool(maps_api_key()))


@app.post("/api/traffic/analyze")
def analyze_trip(request: TripAnalysisRequest) -> dict[str, Any]:
    client = get_maps_client()

    origin = geocode_with_fallback(client, request.origin)
    destination = geocode_with_fallback(client, request.destination)
    live_snapshot = live_route_snapshot(client, origin, destination, request.departure_time)
    selected_metrics = predicted_trip_metrics(
        request,
        live_snapshot["distance_km"],
        live_snapshot["freeflow_minutes"],
        live_snapshot["live_minutes"],
    )
    windows = build_departure_windows(
        request,
        live_snapshot["distance_km"],
        live_snapshot["freeflow_minutes"],
        live_snapshot["live_minutes"],
    )
    best_option = windows[0]
    summary, time_saved = recommendation_summary(best_option, selected_metrics)

    parking_score, parking_level, parking_guidance = parking_profile(request.destination, request.departure_time)
    parking_payload = {
        "score": parking_score,
        "availability": parking_level,
        "guidance": parking_guidance,
    }

    if not request.parking_needed:
        parking_payload = {
            "score": None,
            "availability": "Not requested",
            "guidance": "Parking analysis skipped for this trip.",
        }

    stress_index = int(
        clamp(
            selected_metrics["congestion_score"]
            + (12 if request.commute_style == "lowest_stress" else 0)
            - (6 if request.commute_style == "fastest" else 0),
            10,
            98,
        )
    )

    return {
        "trip": {
            "origin": origin.model_dump(),
            "destination": destination.model_dump(),
            "departure_time": request.departure_time.isoformat(),
            "commute_style": request.commute_style,
        },
        "route": {
            "distance_km": live_snapshot["distance_km"],
            "freeflow_duration_minutes": live_snapshot["freeflow_minutes"],
            "current_duration_minutes": live_snapshot["live_minutes"],
            "predicted_duration_minutes": selected_metrics["predicted_minutes"],
            "delay_minutes": selected_metrics["delay_minutes"],
            "congestion_score": selected_metrics["congestion_score"],
            "congestion_level": selected_metrics["congestion_level"],
            "forecast_basis": selected_metrics["profile_label"],
            "data_source": live_snapshot["source"],
            "polyline": live_snapshot["polyline"],
            "path": live_snapshot["path"],
        },
        "advice": {
            "headline": summary,
            "recommended_departure": best_option,
            "time_saved_minutes": time_saved,
            "stress_index": stress_index,
        },
        "parking": parking_payload,
        "forecast_windows": windows[:4],
    }
