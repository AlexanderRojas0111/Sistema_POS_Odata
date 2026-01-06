# Sistema POS Sabrositas v2.0.0 - Dockerfile de Producción Python 3.13
FROM python:3.13-alpine

# Metadatos actualizados
LABEL maintainer="Sistema POS Sabrositas"
LABEL version="2.0.0"
LABEL description="Sistema de Punto de Venta Sabrositas - Las Arepas Cuadradas"
LABEL python.version="3.13"
LABEL architecture="enterprise"

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_ENV=production
ENV PORT=8000

# Crear usuario no-root
RUN addgroup -g 1000 posuser && adduser -u 1000 -G posuser -s /bin/sh -D posuser

# Instalar dependencias del sistema y actualizar paquetes
RUN apk update && apk upgrade && apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    libffi-dev \
    postgresql-dev \
    curl \
    build-base \
    python3-dev \
    && rm -rf /var/cache/apk/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements e instalar dependencias optimizadas para Python 3.13
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && pip cache purge

# Copiar código de la aplicación
COPY . ./

# Crear directorios necesarios con permisos correctos
RUN mkdir -p logs instance data backups && \
    chmod -R 755 logs instance data backups

# Cambiar permisos
RUN chown -R posuser:posuser /app && \
    chmod -R 755 /app/logs

# Cambiar a usuario no-root
USER posuser

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Comando de inicio - Usar gunicorn en producción optimizado
# Configuración optimizada para producción:
# - worker-class: gthread (mejor para I/O bound)
# - workers: 4 (CPU cores * 2 + 1)
# - threads: 4 (por worker)
# - timeout: 120s
# - keepalive: 5s
# - max-requests: 1000 (prevenir memory leaks)
# - max-requests-jitter: 50
# Para desarrollo: CMD ["python", "main.py"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "gthread", "--threads", "4", "--timeout", "120", "--keep-alive", "5", "--max-requests", "1000", "--max-requests-jitter", "50", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info", "main:app"]