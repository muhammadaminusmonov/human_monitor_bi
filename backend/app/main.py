from fastapi import FastAPI
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


app = FastAPI(title="ASSBI Platform")

app.include_router(city_router)
app.include_router(camera_router)
app.include_router(telemetry_router)
app.include_router(detected_object_router)
app.include_router(anomalies_router)
app.include_router(street)
app.include_router(location)



@app.get("/")
def root():
    return {
        "message": "AI Surveillance + BI Platform Running"
    }


# Create table manualy ---> 创建表手册
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.on_event("startup")
async def startup_event():
    print("AI Detection Model loaded successfully.")