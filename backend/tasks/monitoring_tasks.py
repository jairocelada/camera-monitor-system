import asyncio
from ping3 import ping
from datetime import datetime
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from sqlalchemy import select
from database import AsyncSessionLocal
from models.device import Camera, ConnectivityLog, DeviceStatus
from celery_worker import celery_app
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_single_camera(camera_id: str, ip: str):
    """Revisa una cámara individual"""
    try:
        # Ping con timeout de 2 segundos
        response = ping(ip, timeout=2, unit='ms')
        
        async with AsyncSessionLocal() as session:
            camera = await session.get(Camera, camera_id)
            
            if response is None:
                # No respondió
                camera.status = DeviceStatus.OFFLINE
                camera.packet_loss_percent = 100.0
                camera.response_time_ms = None
                log_status = DeviceStatus.OFFLINE
                latency = None
                packet_loss = 100.0
            else:
                # Respondió
                latency = round(response, 2)
                if latency > 1000:  # Más de 1 segundo = warning
                    camera.status = DeviceStatus.WARNING
                    log_status = DeviceStatus.WARNING
                else:
                    camera.status = DeviceStatus.ONLINE
                    log_status = DeviceStatus.ONLINE
                camera.response_time_ms = latency
                camera.packet_loss_percent = 0.0
                packet_loss = 0.0
            
            camera.last_seen = datetime.utcnow()
            
            # Crear log
            log = ConnectivityLog(
                camera_id=camera_id,
                status=log_status,
                response_time_ms=latency,
                packet_loss=packet_loss,
                hour_bucket=datetime.utcnow().hour
            )
            session.add(log)
            await session.commit()
            
            logger.info(f"✅ Cámara {ip}: {log_status} ({latency}ms)")
            return {
                'camera_id': camera_id,
                'status': log_status,
                'latency': latency
            }
            
    except Exception as e:
        logger.error(f"❌ Error revisando {ip}: {e}")
        raise

@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def check_camera_task(self, camera_id: str, ip_address: str):
    """
    Tarea Celery para revisar una cámara.
    Se ejecuta en el worker, no en la API.
    """
    try:
        # Celery es síncrono, pero nuestro código es async
        # Usamos asyncio.run para ejecutar código async
        result = asyncio.run(check_single_camera(camera_id, ip_address))
        return result
    except Exception as exc:
        logger.error(f"Error en tarea, reintentando: {exc}")
        try:
            raise self.retry(exc=exc)
        except MaxRetriesExceededError:
            logger.error(f"Máximos reintentos alcanzados para {ip_address}")
            return {'error': str(exc), 'camera_id': camera_id}

@celery_app.task
def check_all_cameras():
    """
    Revisa TODAS las cámaras monitoreadas.
    Se ejecuta cada 30 segundos (configurado en celery_worker.py)
    """
    logger.info("🚀 Iniciando revisión de todas las cámaras...")
    
    async def fetch_and_check():
        async with AsyncSessionLocal() as session:
            # Buscar cámaras activas
            result = await session.execute(
                select(Camera).where(Camera.is_monitored == True)
            )
            cameras = result.scalars().all()
            
            logger.info(f"📹 Encontradas {len(cameras)} cámaras para monitorear")
            
            # Encolar tarea individual para cada cámara
            for camera in cameras:
                check_camera_task.delay(str(camera.id), str(camera.ip_address))
            
            return len(cameras)
    
    count = asyncio.run(fetch_and_check())
    return {'cameras_queued': count}