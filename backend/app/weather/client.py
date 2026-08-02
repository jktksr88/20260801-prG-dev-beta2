from __future__ import annotations
import httpx
from app.core.config import settings
from app.weather.climate import fallback_climate

async def search_locations(query: str, language: str="en") -> list[dict]:
    if len(query.strip())<2: return []
    try:
        async with httpx.AsyncClient(timeout=6) as client:
            r=await client.get(f"{settings.open_meteo_geocoding_url}/search",params={"name":query,"count":8,"language":language,"countryCode":"ID"})
            r.raise_for_status()
            return [{"name":x.get("name"),"admin1":x.get("admin1"),"latitude":x.get("latitude"),"longitude":x.get("longitude"),"elevation":x.get("elevation"),"country_code":x.get("country_code")} for x in r.json().get("results",[])]
    except Exception:
        return []

async def get_weather_context(city: str, latitude: float | None, longitude: float | None, elevation_m: float | None=None) -> dict:
    fallback=fallback_climate(city,elevation_m)
    if latitude is None or longitude is None:
        return {**fallback,"provider_available":False,"message":"Weather coordinates unavailable; using broad climate fallback."}
    try:
        async with httpx.AsyncClient(timeout=7) as client:
            r=await client.get(f"{settings.open_meteo_base_url}/forecast",params={"latitude":latitude,"longitude":longitude,"current":"temperature_2m,relative_humidity_2m,precipitation,weather_code","daily":"temperature_2m_max,temperature_2m_min,precipitation_sum","timezone":"auto","forecast_days":7})
            r.raise_for_status(); data=r.json(); cur=data.get("current",{}); daily=data.get("daily",{})
            maxs=daily.get("temperature_2m_max",[]); mins=daily.get("temperature_2m_min",[])
            mean=((sum(maxs)/len(maxs))+(sum(mins)/len(mins)))/2 if maxs and mins else cur.get("temperature_2m",fallback["mean_temperature_c"])
            return {"mean_temperature_c":round(mean,1),"current_temperature_c":cur.get("temperature_2m"),"humidity_percent":cur.get("relative_humidity_2m"),"precipitation_mm":cur.get("precipitation"),"seven_day_rain_mm":round(sum(daily.get("precipitation_sum",[]) or [0]),1),"climate_label":fallback["climate_label"],"confidence":"weather_plus_climate_fallback","provider_available":True}
    except Exception:
        return {**fallback,"provider_available":False,"message":"Weather provider unavailable; using broad climate fallback.","confidence":"reduced"}
