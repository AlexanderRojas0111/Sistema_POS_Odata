# Sistema POS O'Data v2.0.0 - Dockerfile de Producción
FROM python:3.13-alpine3.18

# Metadatos
LABEL maintainer="Sistema POS O'Data"
LABEL version="2.0.0"
LABEL description="Sistema de Punto de Venta O'Data"

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

# Copiar requirements e instalar dependencias
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip cache purge

# Copiar código de la aplicación
COPY . ./

# Crear directorios necesarios
RUN mkdir -p logs instance data

# Cambiar permisos
RUN chown -R posuser:posuser /app

# Cambiar a usuario no-root
USER posuser

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Comando de inicio
CMD ["python", "main.py"]