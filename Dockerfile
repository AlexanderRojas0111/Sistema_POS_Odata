# Etapa de construcción optimizada
FROM python:3.12-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /build

# Instalar dependencias Python
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -U pip setuptools wheel && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Etapa final
FROM python:3.12-slim-bookworm

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    FLASK_APP=app.main:app \
    FLASK_ENV=production \
    PYTHONPATH=/app

# Actualizar y solo instalar dependencias mínimas
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    libpq5 \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && apt-get clean \
 && apt-get autoremove -y

COPY --from=builder /opt/venv /opt/venv

# Crear usuario no root
RUN groupadd -r -g 1001 appuser && \
    useradd -r -u 1001 -g appuser -s /sbin/nologin -d /app appuser

WORKDIR /app
COPY --chown=appuser:appuser . .

RUN mkdir -p logs && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app && \
    find . -type f -name "*.py" -exec chmod 644 {} \; && \
    find . -type d -exec chmod 755 {} \;

RUN if [ -f scripts/entrypoint.sh ]; then \
        cp scripts/entrypoint.sh /entrypoint.sh && \
        chown appuser:appuser /entrypoint.sh && \
        chmod 755 /entrypoint.sh; \
    else \
        echo '#!/bin/bash\nset -e\nexec \"$@\"' > /entrypoint.sh && \
        chown appuser:appuser /entrypoint.sh && \
        chmod 755 /entrypoint.sh; \
    fi

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]