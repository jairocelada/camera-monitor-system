# ==========================================
# ETAPA 1: Base Python 3.13.1
# ==========================================
FROM python:3.13.1-bookworm

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libpcap-dev \
    iputils-ping \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear usuario no-root (seguridad mejorada 2026)
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Directorio de trabajo
WORKDIR /app

# ← NUEVO: Establecer PYTHONPATH para que Celery encuentre módulos
ENV PYTHONPATH=/app:$PYTHONPATH
ENV PYTHONUNBUFFERED=1

# Copiar requirements primero (cache de Docker)
COPY requirements.txt .

# Instalar dependencias Python
# Nuevo: Compilación optimizada para 3.13
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Verificar que existe (debug)
RUN ls -la /app/ && \
    python -c "import sys; print('PYTHONPATH:', sys.path)" && \
    python -c "import celery_worker; print('celery_worker OK')"

# Cambiar a usuario no-root
RUN chown -R appuser:appgroup /app
USER appuser

# ← NUEVO: Asegurar que WORKDIR sigue siendo /app para el usuario
WORKDIR /app

# Puerto
EXPOSE 8000

# Healthcheck mejorado
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Comando con hot-reload para desarrollo
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/app"]