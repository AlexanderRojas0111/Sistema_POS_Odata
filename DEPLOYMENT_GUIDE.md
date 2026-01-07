## Guía de despliegue soportada (Sabrositas POS v2.0.0)

- **Local (desarrollo):** `docker-start.ps1`
  - Requiere `.env` configurado.
  - Ejecuta tests rápidos (`tests/test_basic.py`) antes de construir y levanta servicios con `docker compose`.
  - Health check automático contra `http://localhost:8000/api/v1/health`.

- **Producción / staging (multi-tienda):** `scripts/deploy_production_multistore.ps1`
  - Requiere `.env.production` sin valores de ejemplo.
  - Ejecuta tests (se pueden omitir con `-SkipTests`) y luego construye e inicializa infraestructura, base de datos y monitoreo.

- **Eliminados (legacy):** se retiraron los antiguos scripts de despliegue local/legacy para evitar confusión. Usa exclusivamente los flujos anteriores.

