from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://camera_admin:CamSecure2024!@localhost:5432/camera_monitor')

# Motor asíncrono
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Cambia a True para ver queries SQL en consola
    poolclass=NullPool,  # Para desarrollo, en producción usar pool real
)

# Sesión
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base para modelos
Base = declarative_base()

# Dependencia para FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()