# 📹 Camera Monitor System

Sistema full-stack para monitoreo de cámaras IP con arquitectura distribuida.

## 🏗️ Arquitectura
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   React 19  │────▶│  FastAPI    │────▶│    Redis    │────▶│    Worker   │
│   Vite 6    │◀────│   Python    │◀────│    Cola     │◀────│   Celery    │
│  Frontend   │     │    API      │     │             │     │   (Ping)    │
└─────────────┘     └──────┬──────┘     └─────────────┘     └─────────────┘
│
▼
┌─────────────┐
│  PostgreSQL │
│   (Datos)   │
└─────────────┘
plain
Copy

| Servicio | Tecnología | Puerto | Descripción |
|----------|-----------|--------|-------------|
| Frontend | React 19 + Vite 6 | 5173 | Interfaz de usuario |
| Backend | FastAPI 0.115 + Python 3.13 | 8000 | API REST y lógica de negocio |
| Worker | Celery 5.4 | - | Procesamiento de pings en paralelo |
| Scheduler | Celery Beat | - | Programación de tareas (cada 30s) |
| Base de datos | PostgreSQL 17 | 5432 | Persistencia de datos |
| Cola/Cache | Redis 7.4 | 6379 | Comunicación entre servicios |
| Admin BD | pgAdmin 4 | 5050 | Interfaz web para PostgreSQL |

---

## 🚀 Instalación Rápida

### Requisitos Previos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac) o Docker Engine (Linux)
- [Git](https://git-scm.com/downloads)
- Puertos libres: `5173`, `8000`, `5432`, `5050`, `6379`

### 1. Clonar Repositorio

```bash
git clone https://github.com/TU-USUARIO/camera-monitor-system.git
cd camera-monitor-system
2. Iniciar Servicios
bash
Copy
# Construir e iniciar todos los servicios
docker-compose up --build -d

# Verificar que todo esté corriendo
docker-compose ps
3. Acceder a la Aplicación
Table
Servicio	URL	Credenciales
Frontend	http://localhost:5173	-
API Docs	http://localhost:8000/docs	-
pgAdmin	http://localhost:5050	admin@admin.com / admin
Backend API	http://localhost:8000	-
🗄️ Configuración de pgAdmin (Primera Vez)
Ir a http://localhost:5050
Login: admin@admin.com / admin
Click derecho en Servers → Register → Server
Pestaña General: Name = Camera Monitor DB
Pestaña Connection:
Host: db
Port: 5432
Database: camera_monitor
Username: postgres
Password: postgres
🛠️ Comandos Útiles
Gestión de Servicios
bash
Copy
# Iniciar todo
docker-compose up -d

# Detener todo
docker-compose down

# Detener y eliminar datos (⚠️ Pérdida total)
docker-compose down -v

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f backend
docker-compose logs -f worker
docker-compose logs -f db
Base de Datos
bash
Copy
# Acceder a PostgreSQL CLI
docker-compose exec db psql -U postgres -d camera_monitor

# Ver tablas
\dt

# Ver datos de cámaras
SELECT * FROM cameras;

# Salir
\q
Backend (Python)
bash
Copy
# Ejecutar comandos dentro del contenedor
docker-compose exec backend python -c "print('Hola')"

# Ver versión de Python
docker-compose exec backend python --version

# Instalar nueva dependencia (requiere rebuild)
docker-compose exec backend pip install nombre-paquete
Frontend (Node.js)
bash
Copy
# Ver versión de Node
docker-compose exec frontend node -v

# Ver versión de NPM
docker-compose exec frontend npm -v
💾 Backup y Restauración
Crear Backup
powershell
Copy
# Windows PowerShell
.\backup.ps1
bash
Copy
# Linux/Mac
./backup.sh
Crea archivo backups/YYYY-MM-DD_HH-mm.zip con:
Base de datos completa (SQL)
docker-compose.yml
Variables de entorno (.env)
Restaurar Backup
powershell
Copy
# Windows PowerShell
.\restore.ps1 backups\2026-03-15_21-30.zip
bash
Copy
# Linux/Mac
./restore.sh backups/2026-03-15_21-30.zip
🔧 Variables de Entorno
Crear archivo .env en la raíz (opcional, para personalizar):
env
Copy
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=camera_monitor

# pgAdmin
PGADMIN_DEFAULT_EMAIL=admin@admin.com
PGADMIN_DEFAULT_PASSWORD=admin

# Backend
DATABASE_URL=postgresql://postgres:postgres@db:5432/camera_monitor
REDIS_URL=redis://redis:6379/0

# Frontend
VITE_API_URL=http://localhost:8000
🐛 Solución de Problemas
Puerto ocupado
powershell
Copy
# Ver qué proceso usa el puerto 5432
netstat -ano | findstr 5432

# En Linux/Mac
lsof -i :5432
Contenedor no inicia
bash
Copy
# Ver logs detallados
docker-compose logs nombre-servicio

# Ejemplo
docker-compose logs db
docker-compose logs backend
Reconstruir desde cero
bash
Copy
# Eliminar todo y reconstruir
docker-compose down -v
docker-compose up --build -d
Permisos en Windows
Si ves errores de permisos en PowerShell:
powershell
Copy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
📁 Estructura del Proyecto
plain
Copy
camera-monitor-system/
├── backend/
│   ├── main.py                 # API FastAPI
│   ├── celery_worker.py        # Configuración Celery
│   ├── models.py               # Modelos SQLAlchemy
│   ├── schemas.py              # Pydantic schemas
│   ├── tasks/
│   │   └── monitoring_tasks.py # Tareas de Celery
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/         # Componentes React
│   │   ├── services/           # API calls
│   │   └── App.tsx
│   ├── package.json
│   ├── Dockerfile
│   └── vite.config.ts
├── docker-compose.yml          # Orquestación de servicios
├── backup.ps1                  # Script backup (Windows)
├── backup.sh                   # Script backup (Linux/Mac)
├── restore.ps1                 # Script restore (Windows)
├── restore.sh                  # Script restore (Linux/Mac)
└── README.md                   # Este archivo
🔄 Flujo de Datos
Usuario agrega cámara vía web (React)
Backend guarda en PostgreSQL y encola tarea en Redis
Celery Beat (cada 30s) programa revisión de todas las cámaras
Celery Worker toma tarea de Redis, hace ping a la IP
Worker guarda resultado en PostgreSQL
Frontend muestra estado actualizado al usuario
📊 Escalabilidad
Table
Fase	Cámaras	Acción
MVP	1-50	Docker Compose local
Crecimiento	50-500	docker-compose up --scale worker=5
Producción	500+	Kubernetes o Docker Swarm
🤝 Contribución
Fork el repositorio
Crear rama: git checkout -b feature/nueva-funcionalidad
Commit: git commit -m 'Agrega nueva funcionalidad'
Push: git push origin feature/nueva-funcionalidad
Abrir Pull Request
📄 Licencia
MIT License - Libre para uso personal y comercial.
🆘 Soporte
Issues: GitHub Issues
Email: tu-email@ejemplo.com
Desarrollado con ❤️ usando Python, React y Docker
plain
Copy

---

## 📎 Archivos Adicionales que Debes Crear

### `backup.ps1` (Windows)

```powershell
# backup.ps1
$fecha = Get-Date -Format "yyyy-MM-dd_HH-mm"
$carpeta = "backups/$fecha"

New-Item -ItemType Directory -Force -Path $carpeta

Write-Host "📦 Creando backup..."

# Backup de base de datos
docker-compose exec -T db pg_dump -U postgres camera_monitor > "$carpeta/camera_monitor.sql"

# Backup de configuraciones
Copy-Item docker-compose.yml $carpeta/
if (Test-Path .env) {
    Copy-Item .env $carpeta/
}

# Comprimir
Compress-Archive -Path $carpeta -DestinationPath "$carpeta.zip"
Remove-Item -Recurse $carpeta

Write-Host "✅ Backup creado: $carpeta.zip"
Write-Host "📍 Ubicación: $(Resolve-Path "$carpeta.zip")"
restore.ps1 (Windows)
powershell
Copy
# restore.ps1
param(
    [Parameter(Mandatory=$true)]
    [string]$archivo
)

if (-not (Test-Path $archivo)) {
    Write-Error "❌ Archivo no encontrado: $archivo"
    exit 1
}

Write-Host "📦 Restaurando desde: $archivo"

Expand-Archive -Path $archivo -DestinationPath "temp_restore" -Force

# Encontrar carpeta extraída
$carpeta = Get-ChildItem "temp_restore" -Directory | Select-Object -First 1

# Verificar que existe el SQL
$sqlFile = Join-Path $carpeta.FullName "camera_monitor.sql"
if (-not (Test-Path $sqlFile)) {
    Write-Error "❌ No se encontró archivo SQL en el backup"
    Remove-Item -Recurse temp_restore
    exit 1
}

# Iniciar solo la base de datos
docker-compose up -d db
Write-Host "⏳ Esperando que PostgreSQL inicie..."
Start-Sleep -s 10

# Restaurar datos
Write-Host "🗄️ Restaurando base de datos..."
Get-Content $sqlFile | docker-compose exec -T db psql -U postgres

# Limpiar
Remove-Item -Recurse temp_restore

# Iniciar todo
Write-Host "🚀 Iniciando todos los servicios..."
docker-compose up -d

Write-Host "✅ Restauración completada"
Write-Host "🌐 Frontend: http://localhost:5173"
Write-Host "📊 pgAdmin:  http://localhost:5050"
backup.sh (Linux/Mac)
bash
Copy
#!/bin/bash

FECHA=$(date +"%Y-%m-%d_%H-%M")
CARPETA="backups/$FECHA"

mkdir -p $CARPETA

echo "📦 Creando backup..."

# Backup de base de datos
docker-compose exec -T db pg_dump -U postgres camera_monitor > "$CARPETA/camera_monitor.sql"

# Backup de configuraciones
cp docker-compose.yml $CARPETA/
[ -f .env ] && cp .env $CARPETA/

# Comprimir
tar -czf "$CARPETA.tar.gz" -C backups "$FECHA"
rm -rf $CARPETA

echo "✅ Backup creado: $CARPETA.tar.gz"
restore.sh (Linux/Mac)
bash
Copy
#!/bin/bash

if [ -z "$1" ]; then
    echo "❌ Uso: ./restore.sh backups/2026-03-15_21-30.tar.gz"
    exit 1
fi

ARCHIVO=$1

if [ ! -f "$ARCHIVO" ]; then
    echo "❌ Archivo no encontrado: $ARCHIVO"
    exit 1
fi

echo "📦 Restaurando desde: $ARCHIVO"

# Extraer
tar -xzf $ARCHIVO -C temp_restore

# Encontrar carpeta
CARPETA=$(find temp_restore -mindepth 1 -maxdepth 1 -type d | head -1)

# Restaurar
docker-compose up -d db
echo "⏳ Esperando que PostgreSQL inicie..."
sleep 10

echo "🗄️ Restaurando base de datos..."
cat "$CARPETA/camera_monitor.sql" | docker-compose exec -T db psql -U postgres

# Limpiar
rm -rf temp_restore

# Iniciar todo
echo "🚀 Iniciando todos los servicios..."
docker-compose up -d

echo "✅ Restauración completada"
echo "🌐 Frontend: http://localhost:5173"
echo "📊 pgAdmin:  http://localhost:5050"
✅ Checklist Final
Table
Archivo	Propósito
README.md	Documentación completa
backup.ps1 / backup.sh	Crear backups fácilmente
restore.ps1 / restore.sh	Restaurar en nuevo PC
.gitignore	Evitar subir datos sensibles
