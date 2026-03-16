from sqlalchemy import Column, String, DateTime, Float, Boolean, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID, INET, MACADDR, JSONB
from sqlalchemy.sql import func
import uuid
import enum

from database import Base

class DeviceStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    WARNING = "warning"
    UNREACHABLE = "unreachable"
    MAINTENANCE = "maintenance"

class DeviceType(str, enum.Enum):
    CAMERA = "camera"
    ROUTER = "router"
    SWITCH = "switch"
    SERVER = "server"
    UNKNOWN = "unknown"

class Camera(Base):
    __tablename__ = "cameras"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    ip_address = Column(INET, nullable=False, unique=True, index=True)
    mac_address = Column(MACADDR, nullable=True)
    
    # Información de la cámara
    brand = Column(String(50))  # Hikvision, Dahua, Axis, etc.
    model = Column(String(100))
    location = Column(String(200))
    device_type = Column(Enum(DeviceType), default=DeviceType.CAMERA)
    
    # Estado actual
    status = Column(Enum(DeviceStatus), default=DeviceStatus.OFFLINE)
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    response_time_ms = Column(Float)
    packet_loss_percent = Column(Float, default=100.0)
    
    # Configuración
    is_monitored = Column(Boolean, default=True)
    config = Column(JSONB, default={})  # Resolución, FPS, etc.
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Camera {self.name} ({self.ip_address}) - {self.status}>"

class ConnectivityLog(Base):
    __tablename__ = "connectivity_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Datos de la prueba
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    status = Column(Enum(DeviceStatus))
    response_time_ms = Column(Float)
    packet_loss = Column(Float)
    error_message = Column(String(500))
    
    # Para agregaciones rápidas
    hour_bucket = Column(Integer)  # 0-23
    
    def __repr__(self):
        return f"<Log {self.camera_id} at {self.timestamp} - {self.status}>"