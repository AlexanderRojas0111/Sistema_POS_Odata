# Utiliza una imagen oficial de Python
FROM python:3.9-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de requerimientos y la app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Expone el puerto de la app
EXPOSE 5000

# Comando para ejecutar la app en producción
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app.main:app"] 