from __future__ import annotations
from contextlib import asynccontextmanager
from pathlib import Path
import logging, time, uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect
from app.core.config import settings
from app.core.logging import configure_logging
from app.database.session import engine, SessionLocal
from app.database.seed import seed_crops
from app.models import CropProfile
from app.api.router import api_router

configure_logging(settings.log_level)
logger=logging.getLogger("groe")

@asynccontextmanager
async def lifespan(app:FastAPI):
    if settings.auto_seed and inspect(engine).has_table("crop_profiles"):
        with SessionLocal() as db:
            try: seed_crops(db)
            except Exception: logger.exception("Automatic seed check failed")
    yield

app=FastAPI(title="GROE API",version="1.0.0",lifespan=lifespan,docs_url="/api/docs",openapi_url="/api/openapi.json")
app.add_middleware(CORSMiddleware,allow_origins=list(settings.cors_origins),allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

@app.middleware("http")
async def request_context(request:Request,call_next):
    request_id=request.headers.get("X-Request-ID",str(uuid.uuid4()))
    start=time.perf_counter()
    try:
        response=await call_next(request)
    except Exception:
        logger.exception("Unhandled request error",extra={"request_id":request_id})
        return JSONResponse(status_code=500,content={"detail":"An unexpected error occurred","request_id":request_id})
    response.headers["X-Request-ID"]=request_id
    response.headers["X-Content-Type-Options"]="nosniff"
    response.headers["Referrer-Policy"]="strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"]="camera=(), microphone=(), geolocation=(self)"
    logger.info(f"{request.method} {request.url.path} {response.status_code} {round((time.perf_counter()-start)*1000,1)}ms",extra={"request_id":request_id})
    return response

app.include_router(api_router)

static_dir=Path(__file__).resolve().parent/"static"
if static_dir.exists():
    assets=static_dir/"assets"
    if assets.exists(): app.mount("/assets",StaticFiles(directory=assets),name="assets")
    @app.get("/{full_path:path}",include_in_schema=False)
    async def spa(full_path:str):
        candidate=static_dir/full_path
        if full_path and candidate.is_file(): return FileResponse(candidate)
        return FileResponse(static_dir/"index.html")
else:
    @app.get("/",include_in_schema=False)
    def root(): return {"name":"GROE API","message":"Frontend build is not present. Run the Vite build or use Docker."}
