-- Script de inicialización de base de datos PostgreSQL
-- Sistema POS Sabrositas v2.0.0 - Producción Multi-Tienda
-- ========================================================

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Configurar parámetros de la base de datos
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
-- Nota: pg_stat_statements.track requiere que la librería esté precargada y un reinicio.
-- Se omite para evitar fallos durante la inicialización en contenedores base.
-- ALTER SYSTEM SET pg_stat_statements.track = 'all';
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_min_duration_statement = 1000;

-- Crear esquemas
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS reporting;
CREATE SCHEMA IF NOT EXISTS monitoring;

-- Configurar usuario de aplicación con permisos específicos
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'pos_app_user') THEN
        CREATE USER pos_app_user WITH PASSWORD 'PosApp2024Secure!';
    END IF;
END
$$;

-- Otorgar permisos al usuario de aplicación
GRANT USAGE ON SCHEMA public TO pos_app_user;
GRANT USAGE ON SCHEMA audit TO pos_app_user;
GRANT USAGE ON SCHEMA reporting TO pos_app_user;
GRANT CREATE ON SCHEMA public TO pos_app_user;
GRANT CREATE ON SCHEMA audit TO pos_app_user;
GRANT CREATE ON SCHEMA reporting TO pos_app_user;

-- Configurar timezone
SET timezone = 'America/Bogota';

-- Crear tabla de auditoría general
CREATE TABLE IF NOT EXISTS audit.system_audit (
    id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    operation VARCHAR(10) NOT NULL,
    user_id INTEGER,
    user_name VARCHAR(100),
    old_values JSONB,
    new_values JSONB,
    changed_fields TEXT[],
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    additional_info JSONB
);

-- Índices para auditoría
CREATE INDEX IF NOT EXISTS idx_audit_table_name ON audit.system_audit(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit.system_audit(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit.system_audit(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_operation ON audit.system_audit(operation);

-- Crear tabla de métricas de rendimiento
CREATE TABLE IF NOT EXISTS monitoring.performance_metrics (
    id BIGSERIAL PRIMARY KEY,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    response_time_ms INTEGER NOT NULL,
    status_code INTEGER NOT NULL,
    user_id INTEGER,
    store_id INTEGER,
    request_size INTEGER,
    response_size INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    additional_data JSONB
);

-- Índices para métricas
CREATE INDEX IF NOT EXISTS idx_metrics_endpoint ON monitoring.performance_metrics(endpoint);
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON monitoring.performance_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_metrics_store_id ON monitoring.performance_metrics(store_id);

-- Crear tabla de logs de seguridad
CREATE TABLE IF NOT EXISTS audit.security_events (
    id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'INFO',
    user_id INTEGER,
    username VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    description TEXT NOT NULL,
    additional_data JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para eventos de seguridad
CREATE INDEX IF NOT EXISTS idx_security_event_type ON audit.security_events(event_type);
CREATE INDEX IF NOT EXISTS idx_security_severity ON audit.security_events(severity);
CREATE INDEX IF NOT EXISTS idx_security_timestamp ON audit.security_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_security_user_id ON audit.security_events(user_id);

-- Crear vistas de reporte para análisis
CREATE OR REPLACE VIEW reporting.daily_sales_summary AS
SELECT 
    s.store_id,
    st.name as store_name,
    st.code as store_code,
    DATE(s.created_at) as sale_date,
    COUNT(*) as total_transactions,
    SUM(s.total) as total_sales,
    AVG(s.total) as average_transaction,
    COUNT(DISTINCT s.user_id) as unique_cashiers
FROM sales s
JOIN stores st ON s.store_id = st.id
WHERE s.status = 'completed'
GROUP BY s.store_id, st.name, st.code, DATE(s.created_at)
ORDER BY sale_date DESC, total_sales DESC;

-- Crear vista de inventario crítico
CREATE OR REPLACE VIEW reporting.critical_inventory AS
SELECT 
    sp.store_id,
    s.name as store_name,
    s.code as store_code,
    p.id as product_id,
    p.name as product_name,
    sp.current_stock,
    sp.min_stock,
    sp.reorder_point,
    CASE 
        WHEN sp.current_stock <= 0 THEN 'OUT_OF_STOCK'
        WHEN sp.current_stock <= sp.min_stock THEN 'LOW_STOCK'
        WHEN sp.current_stock <= sp.reorder_point THEN 'REORDER_NEEDED'
        ELSE 'ADEQUATE'
    END as stock_status
FROM store_products sp
JOIN stores s ON sp.store_id = s.id
JOIN products p ON sp.product_id = p.id
WHERE sp.is_available = true 
  AND s.is_active = true 
  AND p.is_active = true
  AND sp.current_stock <= sp.reorder_point
ORDER BY 
    CASE 
        WHEN sp.current_stock <= 0 THEN 1
        WHEN sp.current_stock <= sp.min_stock THEN 2
        WHEN sp.current_stock <= sp.reorder_point THEN 3
        ELSE 4
    END,
    sp.current_stock ASC;

-- Crear función para auditoría automática
CREATE OR REPLACE FUNCTION audit.audit_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
    old_data JSONB;
    new_data JSONB;
    changed_fields TEXT[];
BEGIN
    -- Preparar datos para auditoría
    IF TG_OP = 'DELETE' THEN
        old_data = to_jsonb(OLD);
        new_data = NULL;
    ELSIF TG_OP = 'INSERT' THEN
        old_data = NULL;
        new_data = to_jsonb(NEW);
    ELSE -- UPDATE
        old_data = to_jsonb(OLD);
        new_data = to_jsonb(NEW);
        
        -- Identificar campos cambiados
        SELECT array_agg(key)
        INTO changed_fields
        FROM jsonb_each(old_data) old_kv
        JOIN jsonb_each(new_data) new_kv ON old_kv.key = new_kv.key
        WHERE old_kv.value IS DISTINCT FROM new_kv.value;
    END IF;
    
    -- Insertar registro de auditoría
    INSERT INTO audit.system_audit (
        table_name,
        operation,
        old_values,
        new_values,
        changed_fields,
        additional_info
    ) VALUES (
        TG_TABLE_NAME,
        TG_OP,
        old_data,
        new_data,
        changed_fields,
        jsonb_build_object(
            'transaction_id', txid_current(),
            'schema', TG_TABLE_SCHEMA
        )
    );
    
    -- Retornar el registro apropiado
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Crear función de limpieza de datos antiguos
CREATE OR REPLACE FUNCTION maintenance.cleanup_old_data()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
    temp_count INTEGER;
BEGIN
    -- Limpiar auditoría mayor a 1 año
    DELETE FROM audit.system_audit 
    WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '1 year';
    GET DIAGNOSTICS temp_count = ROW_COUNT;
    deleted_count := deleted_count + temp_count;
    
    -- Limpiar métricas mayores a 6 meses
    DELETE FROM monitoring.performance_metrics 
    WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '6 months';
    GET DIAGNOSTICS temp_count = ROW_COUNT;
    deleted_count := deleted_count + temp_count;
    
    -- Limpiar eventos de seguridad mayores a 2 años
    DELETE FROM audit.security_events 
    WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '2 years'
      AND severity NOT IN ('CRITICAL', 'HIGH');
    GET DIAGNOSTICS temp_count = ROW_COUNT;
    deleted_count := deleted_count + temp_count;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Crear esquema de mantenimiento
CREATE SCHEMA IF NOT EXISTS maintenance;

-- Otorgar permisos de mantenimiento
GRANT USAGE ON SCHEMA maintenance TO pos_app_user;
GRANT EXECUTE ON FUNCTION maintenance.cleanup_old_data() TO pos_app_user;

-- Configurar parámetros de rendimiento
ALTER DATABASE pos_odata SET work_mem = '32MB';
ALTER DATABASE pos_odata SET shared_buffers = '256MB';
ALTER DATABASE pos_odata SET effective_cache_size = '1GB';
ALTER DATABASE pos_odata SET random_page_cost = 1.1;

-- Configurar logging
ALTER DATABASE pos_odata SET log_min_duration_statement = 1000;
ALTER DATABASE pos_odata SET log_statement = 'mod';
ALTER DATABASE pos_odata SET log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h ';

-- Crear índices de texto completo para búsquedas
CREATE INDEX IF NOT EXISTS idx_products_search 
ON products USING gin(to_tsvector('spanish', name || ' ' || description));

CREATE INDEX IF NOT EXISTS idx_stores_search 
ON stores USING gin(to_tsvector('spanish', name || ' ' || address));

-- Configurar estadísticas automáticas
ALTER DATABASE pos_odata SET track_activities = on;
ALTER DATABASE pos_odata SET track_counts = on;
ALTER DATABASE pos_odata SET track_io_timing = on;
ALTER DATABASE pos_odata SET track_functions = 'all';

-- Comentarios para documentación
COMMENT ON SCHEMA audit IS 'Esquema para auditoría y trazabilidad del sistema';
COMMENT ON SCHEMA reporting IS 'Esquema para vistas y reportes de análisis';
COMMENT ON SCHEMA monitoring IS 'Esquema para métricas de rendimiento y monitoreo';
COMMENT ON TABLE audit.system_audit IS 'Registro completo de cambios en el sistema';
COMMENT ON TABLE monitoring.performance_metrics IS 'Métricas de rendimiento de endpoints';
COMMENT ON TABLE audit.security_events IS 'Eventos de seguridad y acceso';

-- Mensaje de finalización
DO $$
BEGIN
    RAISE NOTICE 'Base de datos inicializada correctamente para Sistema POS Sabrositas v2.0.0';
    RAISE NOTICE 'Esquemas creados: public, audit, reporting, monitoring, maintenance';
    RAISE NOTICE 'Usuario de aplicación: pos_app_user configurado';
    RAISE NOTICE 'Extensiones habilitadas: uuid-ossp, pg_trgm, btree_gin';
END $$;