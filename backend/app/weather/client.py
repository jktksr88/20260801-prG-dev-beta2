from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import httpx

from app.core.config import settings
from app.weather.climate import fallback_climate
from app.weather.indonesia_locations import search_local_locations

_CACHE_TTL_SECONDS = 600
_location_cache: dict[tuple[str, str], tuple[float, list[dict[str, Any]]]] = {}
_weather_cache: dict[tuple[float, float], tuple[float, dict[str, Any]]] = {}

WEATHER_LABELS = {
    0: ("Clear sky", "Cerah"),
    1: ("Mainly clear", "Sebagian besar cerah"),
    2: ("Partly cloudy", "Berawan sebagian"),
    3: ("Overcast", "Mendung"),
    45: ("Fog", "Berkabut"),
    48: ("Rime fog", "Kabut tebal"),
    51: ("Light drizzle", "Gerimis ringan"),
    53: ("Drizzle", "Gerimis"),
    55: ("Heavy drizzle", "Gerimis lebat"),
    61: ("Light rain", "Hujan ringan"),
    63: ("Rain", "Hujan"),
    65: ("Heavy rain", "Hujan lebat"),
    80: ("Light showers", "Hujan lokal ringan"),
    81: ("Showers", "Hujan lokal"),
    82: ("Heavy showers", "Hujan lokal lebat"),
    95: ("Thunderstorm", "Badai petir"),
    96: ("Thunderstorm with hail", "Badai petir dengan hujan es"),
    99: ("Severe thunderstorm", "Badai petir kuat"),
}


def _weather_label(code: int | None, language: str = "en") -> str:
    labels = WEATHER_LABELS.get(int(code or -1), ("Current conditions", "Kondisi saat ini"))
    return labels[1] if language == "id" else labels[0]


def _cached(cache: dict, key: Any) -> Any | None:
    item = cache.get(key)
    if not item:
        return None
    created, value = item
    if time.monotonic() - created > _CACHE_TTL_SECONDS:
        cache.pop(key, None)
        return None
    return value


async def search_locations(query: str, language: str = "en") -> list[dict[str, Any]]:
    cleaned = query.strip()
    if len(cleaned) < 3:
        return []
    key = (cleaned.lower(), language)
    cached = _cached(_location_cache, key)
    if cached is not None:
        return cached

    local_items = search_local_locations(cleaned, limit=10)
    remote_items: list[dict[str, Any]] = []
    try:
        async with httpx.AsyncClient(timeout=8, headers={"User-Agent": "GROE-beta/7.0"}) as client:
            response = await client.get(
                f"{settings.open_meteo_geocoding_url}/search",
                params={
                    "name": cleaned,
                    "count": 10,
                    "language": language,
                    "countryCode": "ID",
                    "format": "json",
                },
            )
            response.raise_for_status()
            for row in response.json().get("results", []):
                name = row.get("name")
                if not name or row.get("latitude") is None or row.get("longitude") is None:
                    continue
                admin1 = row.get("admin1")
                admin2 = row.get("admin2")
                parts = [part for part in [name, admin2, admin1] if part]
                remote_items.append(
                    {
                        "id": row.get("id"),
                        "name": name,
                        "admin1": admin1,
                        "admin2": admin2,
                        "display_name": ", ".join(dict.fromkeys(parts)),
                        "latitude": row.get("latitude"),
                        "longitude": row.get("longitude"),
                        "elevation": row.get("elevation"),
                        "country_code": row.get("country_code") or "ID",
                        "source": "open_meteo",
                    }
                )
    except (httpx.HTTPError, ValueError, TypeError):
        remote_items = []

    merged: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for item in [*remote_items, *local_items]:
        identity = (str(item.get("name", "")).lower(), str(item.get("admin1", "")).lower())
        if identity in seen:
            continue
        seen.add(identity)
        merged.append(item)
        if len(merged) >= 10:
            break
    _location_cache[key] = (time.monotonic(), merged)
    return merged


async def get_weather_context(
    city: str,
    latitude: float | None,
    longitude: float | None,
    elevation_m: float | None = None,
    language: str = "en",
) -> dict[str, Any]:
    fallback = fallback_climate(city, elevation_m)
    if latitude is None or longitude is None:
        return {
            **fallback,
            "provider": "climate_fallback",
            "provider_available": False,
            "message": "Weather coordinates unavailable; using broad climate fallback.",
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "weather_label": "Broad climate estimate" if language == "en" else "Perkiraan iklim umum",
        }

    key = (round(float(latitude), 4), round(float(longitude), 4))
    cached = _cached(_weather_cache, key)
    if cached is not None:
        return cached

    try:
        async with httpx.AsyncClient(timeout=10, headers={"User-Agent": "GROE-beta/7.0"}) as client:
            response = await client.get(
                f"{settings.open_meteo_base_url}/forecast",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": (
                        "temperature_2m,relative_humidity_2m,apparent_temperature,"
                        "precipitation,rain,weather_code,cloud_cover,wind_speed_10m,"
                        "wind_direction_10m,wind_gusts_10m"
                    ),
                    "daily": (
                        "temperature_2m_max,temperature_2m_min,precipitation_sum,"
                        "precipitation_probability_max,wind_speed_10m_max"
                    ),
                    "timezone": "auto",
                    "forecast_days": 7,
                },
            )
            response.raise_for_status()
            data = response.json()
            current = data.get("current", {})
            daily = data.get("daily", {})
            maxs = [float(v) for v in daily.get("temperature_2m_max", []) if v is not None]
            mins = [float(v) for v in daily.get("temperature_2m_min", []) if v is not None]
            mean = (
                (sum(maxs) / len(maxs) + sum(mins) / len(mins)) / 2
                if maxs and mins
                else current.get("temperature_2m", fallback["mean_temperature_c"])
            )
            rain_values = [float(v or 0) for v in daily.get("precipitation_sum", [])]
            rain_probability = [int(v or 0) for v in daily.get("precipitation_probability_max", [])]
            code = current.get("weather_code")
            result = {
                "provider": "open_meteo",
                "provider_available": True,
                "updated_at": current.get("time"),
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "timezone": data.get("timezone"),
                "latitude": data.get("latitude", latitude),
                "longitude": data.get("longitude", longitude),
                "elevation_m": data.get("elevation", elevation_m),
                "mean_temperature_c": round(float(mean), 1),
                "current_temperature_c": current.get("temperature_2m"),
                "apparent_temperature_c": current.get("apparent_temperature"),
                "humidity_percent": current.get("relative_humidity_2m"),
                "precipitation_mm": current.get("precipitation"),
                "rain_mm": current.get("rain"),
                "cloud_cover_percent": current.get("cloud_cover"),
                "wind_speed_kmh": current.get("wind_speed_10m"),
                "wind_direction_degrees": current.get("wind_direction_10m"),
                "wind_gust_kmh": current.get("wind_gusts_10m"),
                "weather_code": code,
                "weather_label": _weather_label(code, language),
                "seven_day_rain_mm": round(sum(rain_values), 1),
                "max_rain_probability_percent": max(rain_probability, default=0),
                "climate_label": fallback["climate_label"],
                "confidence": "weather_plus_climate_fallback",
            }
            _weather_cache[key] = (time.monotonic(), result)
            return result
    except (httpx.HTTPError, ValueError, TypeError):
        return {
            **fallback,
            "provider": "climate_fallback",
            "provider_available": False,
            "message": "Weather provider unavailable; using broad climate fallback.",
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "weather_label": "Broad climate estimate" if language == "en" else "Perkiraan iklim umum",
            "confidence": "reduced",
        }
