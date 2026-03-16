from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from contextlib import asynccontextmanager
import os
import logging

from database import get_db, engine, Base
from models.device import Camera, ConnectivityLog, DeviceStatus
from tasks.monitoring_tasks import check_camera_task, check_all_cameras
from pydantic import BaseModel, Field, field_validator  # ← Agregar field_validator
from typing import List, Optional
from datetime import datetime
import uuid

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear tablas al iniciar
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Iniciando aplicación...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Tablas creadas/verificadas")
    yield
    logger.info("👋 Cerrando aplicación...")

app = FastAPI(
    title="Camera Monitor API",
    description="API para monitoreo de cámaras IP",
    version="1.0.0",
    lifespan=lifespan
)

# CORS para que React pueda hablar con la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas Pydantic
class CameraCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    # ip_address: str = Field(..., regex=r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    ip_address: str = Field(..., pattern=r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    location: Optional[str] = None
    brand: Optional[str] = None

class CameraResponse(BaseModel):
    id: uuid.UUID
    name: str
    ip_address: str
    status: DeviceStatus
    last_seen: Optional[datetime]
    response_time_ms: Optional[float]
    location: Optional[str] = None  # ← También agregar si lo usas
    
    # ← NUEVO: Validador para convertir IPv4Address a string
    @field_validator('ip_address', mode='before')
    @classmethod
    def convert_ip_to_string(cls, v):
        if v is None:
            return None
        return str(v)  # IPv4Address('192.168.0.1') → '192.168.0.1'

# Endpoints
@app.get("/")
async def root():
    return {
        "message": "Camera Monitor API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.post("/cameras", response_model=CameraResponse)
async def create_camera(
    camera: CameraCreate,
    db: AsyncSession = Depends(get_db)
):
    """Crear nueva cámara"""
    # Verificar si IP ya existe
    result = await db.execute(
        select(Camera).where(Camera.ip_address == camera.ip_address)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="IP ya existe")
    
    db_camera = Camera(
        name=camera.name,
        ip_address=camera.ip_address,
        location=camera.location,
        brand=camera.brand
    )
    db.add(db_camera)
    await db.commit()
    await db.refresh(db_camera)
    
    logger.info(f"📹 Cámara creada: {db_camera.name} ({db_camera.ip_address})")
    return db_camera

@app.get("/cameras", response_model=List[CameraResponse])
async def list_cameras(
    status: Optional[DeviceStatus] = None,
    db: AsyncSession = Depends(get_db)
):
    """Listar todas las cámaras, opcionalmente filtrar por estado"""
    query = select(Camera)
    if status:
        query = query.where(Camera.status == status)
    
    result = await db.execute(query)
    cameras = result.scalars().all()
    return cameras

@app.get("/cameras/{camera_id}", response_model=CameraResponse)
async def get_camera(camera_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Obtener detalle de una cámara"""
    camera = await db.get(Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    return camera

@app.post("/cameras/{camera_id}/check")
async def check_camera_now(
    camera_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Revisar cámara ahora mismo (en background)"""
    camera = await db.get(Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    
    # Encolar tarea
    task = check_camera_task.delay(str(camera.id), str(camera.ip_address))
    
    return {
        "message": "Revisión encolada",
        "task_id": task.id,
        "camera": camera.name
    }

@app.post("/cameras/check-all")
async def check_all_now(background_tasks: BackgroundTasks):
    """Revisar todas las cámaras ahora"""
    task = check_all_cameras.delay()
    return {
        "message": "Revisión masiva iniciada",
        "task_id": task.id
    }

@app.get("/cameras/{camera_id}/logs")
async def get_camera_logs(
    camera_id: uuid.UUID,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Obtener historial de conectividad"""
    result = await db.execute(
        select(ConnectivityLog)
        .where(ConnectivityLog.camera_id == camera_id)
        .order_by(ConnectivityLog.timestamp.desc())
        .limit(limit)
    )
    logs = result.scalars().all()
    return logs

@app.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Estadísticas generales"""
    # Contar por estado
    result = await db.execute(
        select(Camera.status, func.count(Camera.id))
        .group_by(Camera.status)
    )
    status_counts = {status.value: count for status, count in result.all()}
    
    total = sum(status_counts.values())
    
    return {
        "total_cameras": total,
        "by_status": status_counts,
        "online_percent": round((status_counts.get('online', 0) / total * 100), 2) if total > 0 else 0
    }

from sqlalchemy import func

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)