# Dockerfile para la aplicación Flask (Backend)

# Aceptar la versión de Python como un argumento de construcción
ARG PYTHON_VERSION=3.13

# Usar la versión de Python especificada en la imagen base
FROM python:${PYTHON_VERSION}-slim-bookworm

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto y definir el comando de inicio
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app.main:app"]