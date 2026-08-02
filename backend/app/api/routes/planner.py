from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.planner import PlannerInput
from app.planning.optimizer import generate_recommendations
from app.spatial.geometry import GeometryError
from app.weather.client import get_weather_context

router=APIRouter(prefix="/planner",tags=["planner"])

@router.post("/recommendations")
async def recommendations(payload:PlannerInput,db:Session=Depends(get_db)):
    weather=await get_weather_context(payload.location.city,payload.location.latitude,payload.location.longitude,payload.location.elevation_m)
    try: return generate_recommendations(db,payload,weather)
    except GeometryError as exc: raise HTTPException(422,{"code":"INVALID_PLOT_GEOMETRY","message":str(exc)})
