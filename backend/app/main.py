from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine
from app.models.base import Base
import app.models
from app.api.v1.routers.city import router as city_router
from app.api.v1.routers.camera import router as camera_router
from app.api.v1.routers.crowd_telemetry import router as telemetry_router
from app.api.v1.routers.detected_object import router as detected_object_router
from app.api.v1.routers.anomalies import router as anomalies_router
from app.api.v1.routers.street import router as street
from app.api.v1.routers.location import router as location
from app.api.v1.routers.stream import router as stream_router   # <-- YOLO WebSocket

app = FastAPI(title="ASSBI Platform")

# CORS — нужен для Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(city_router)
app.include_router(camera_router)
app.include_router(telemetry_router)
app.include_router(detected_object_router)
app.include_router(anomalies_router)
app.include_router(street)
app.include_router(location)
app.include_router(stream_router)   # <-- WebSocket стрим


@app.get("/")
def root():
    return {"message": "AI Surveillance + BI Platform Running"}


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)