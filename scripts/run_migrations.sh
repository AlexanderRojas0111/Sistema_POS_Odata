#!/bin/bash

# Esperar a que la base de datos esté lista
echo "Esperando a que la base de datos esté lista..."
sleep 10

# Ejecutar migraciones
echo "Ejecutando migraciones..."
flask db upgrade

# Inicializar datos básicos
echo "Inicializando datos básicos..."
python scripts/init_db.py

echo "Migraciones completadas." 