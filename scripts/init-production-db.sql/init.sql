-- Script de inicialización de la base de datos de producción
-- Sistema POS Odata

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Configurar timezone
SET timezone = 'UTC';

-- Crear índices de rendimiento
CREATE INDEX IF NOT EXISTS idx_products_name ON products USING gin(name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(date);
CREATE INDEX IF NOT EXISTS idx_inventory_movements_date ON inventory_movements(movement_date);

-- Configurar autovacuum para mantenimiento automático
ALTER SYSTEM SET autovacuum = on;
ALTER SYSTEM SET autovacuum_max_workers = 3;
ALTER SYSTEM SET autovacuum_naptime = '1min';

-- Configurar checkpoint para mejor rendimiento
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';

-- Recargar configuración
SELECT pg_reload_conf();
