# Etapa de construcción
FROM python:3.12-slim-bookworm AS builder

# Establecer variables de entorno para seguridad y optimización
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Actualizar paquetes del sistema primero para corregir vulnerabilidades
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Establecer directorio de trabajo
WORKDIR /build

# Copiar requirements.txt
COPY requirements.txt .

# Instalar dependencias de Python en un entorno virtual
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -U pip setuptools wheel && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Etapa final
FROM python:3.12-slim-bookworm

# Establecer variables de entorno
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    FLASK_APP=app.main:app \
    FLASK_ENV=production \
    PYTHONPATH=/app

# Actualizar todos los paquetes del sistema para corregir vulnerabilidades críticas
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    curl \
    netcat-openbsd \
    libpq5 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && apt-get autoremove -y

# Copiar el entorno virtual desde la etapa de construcción
COPY --from=builder /opt/venv /opt/venv

# Crear usuario no root para seguridad
RUN groupadd -r -g 1001 appuser && \
    useradd -r -u 1001 -g appuser -s /sbin/nologin -d /app appuser

# Establecer directorio de trabajo
WORKDIR /app

# Copiar el código de la aplicación
COPY --chown=appuser:appuser . .

# Crear directorio para logs y establecer permisos
RUN mkdir -p logs && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app && \
    find . -type f -name "*.py" -exec chmod 644 {} \; && \
    find . -type d -exec chmod 755 {} \;

# Verificar que el script de entrypoint existe y establecer permisos
RUN if [ -f scripts/entrypoint.sh ]; then \
        cp scripts/entrypoint.sh /entrypoint.sh && \
        chown appuser:appuser /entrypoint.sh && \
        chmod 755 /entrypoint.sh; \
    else \
        echo '#!/bin/bash\nset -e\nexec "$@"' > /entrypoint.sh && \
        chown appuser:appuser /entrypoint.sh && \
        chmod 755 /entrypoint.sh; \
    fi

# Cambiar al usuario no root
USER appuser

# Exponer puerto
EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Comando para ejecutar la aplicación
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
