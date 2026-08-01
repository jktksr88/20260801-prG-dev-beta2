from fastapi import APIRouter, Query
from app.weather.client import search_locations, get_weather_context

router=APIRouter(prefix="/weather",tags=["weather"])

@router.get("/locations")
async def locations(q:str=Query(min_length=2,max_length=100),language:str="en"):
    return {"items":await search_locations(q,language)}

@router.get("/context")
async def context(city:str,latitude:float|None=None,longitude:float|None=None,elevation_m:float|None=None):
    return await get_weather_context(city,latitude,longitude,elevation_m)
