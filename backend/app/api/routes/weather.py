from fastapi import APIRouter, Query

from app.weather.client import get_weather_context, search_locations

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/locations")
async def locations(
    q: str = Query(min_length=3, max_length=100),
    language: str = Query(default="en", pattern="^(en|id)$"),
):
    return {"items": await search_locations(q, language)}


@router.get("/context")
async def context(
    city: str,
    latitude: float | None = None,
    longitude: float | None = None,
    elevation_m: float | None = None,
    language: str = Query(default="en", pattern="^(en|id)$"),
):
    return await get_weather_context(city, latitude, longitude, elevation_m, language)
