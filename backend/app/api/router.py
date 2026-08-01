from fastapi import APIRouter
from app.api.routes import auth, plants, planner, weather, plans, diary, health

api_router=APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(plants.router)
api_router.include_router(planner.router)
api_router.include_router(weather.router)
api_router.include_router(plans.router)
api_router.include_router(plans.public_router)
api_router.include_router(diary.router)
api_router.include_router(health.router)
