-- Extensiones útiles
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Tabla de cámaras (ya la crea SQLAlchemy, pero por si acaso)
-- Nota: SQLAlchemy creará las tablas automáticamente, 
-- este script es para datos iniciales o configuraciones

-- Datos de ejemplo (opcional, quitar en producción)
-- INSERT INTO cameras (id, name, ip_address, location, brand, status) 
-- VALUES 
--   (gen_random_uuid(), 'Cámara Test', '192.168.1.100', 'Oficina', 'Hikvision', 'offline');