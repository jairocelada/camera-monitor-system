from celery import Celery
from celery.signals import worker_ready
import os

# Leer variables de entorno
broker_url = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

# Crear app Celery
celery_app = Celery(
    'camera_monitor',
    broker=broker_url,
    backend=result_backend,
    include=['tasks.monitoring_tasks']  # Donde están las tareas
)

# Configuración
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30,  # Máximo 30 segundos por tarea
    worker_prefetch_multiplier=1,  # Un worker toma 1 tarea a la vez
    broker_connection_retry_on_startup=True,
)

# Beat schedule (el "reloj")
celery_app.conf.beat_schedule = {
    'check-all-cameras-every-30-seconds': {
        'task': 'tasks.monitoring_tasks.check_all_cameras',
        'schedule': 30.0,  # Segundos
    },
}

@worker_ready.connect
def at_start(sender, **k):
    """Se ejecuta cuando el worker arranca"""
    print("✅ Worker listo para monitorear cámaras!")
    # ← NUEVO: Verificar que se creó correctamente al importar
    print(f"Celery app created: {celery_app}")