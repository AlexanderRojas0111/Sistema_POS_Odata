# 🐳 COMANDOS DOCKER PARA DESPLIEGUE

## Comandos Manuales (Recomendado):

### 1. Detener servicios existentes:
```bash
docker-compose down
docker stop pos-backend pos-frontend 2>/dev/null || true
docker rm pos-backend pos-frontend 2>/dev/null || true
```

### 2. Iniciar Backend:
```bash
docker run -d --name pos-backend -p 5000:5000 -v %cd%:/app -w /app python:3.13-slim sh -c "pip install -r requirements.txt && python run_server.py"
```

### 3. Iniciar Frontend:
```bash
docker run -d --name pos-frontend -p 5173:5173 -v %cd%/Sistema_POS_Odata_nuevo/frontend:/app -w /app node:22-alpine sh -c "npm install && npm run dev -- --host 0.0.0.0 --port 5173"
```

### 4. Verificar estado:
```bash
docker ps
curl http://localhost:5000/health
```

## URLs del Sistema:
- **Backend**: http://localhost:5000
- **Frontend**: http://localhost:5173
- **Health Check**: http://localhost:5000/health

## Comandos de gestión:
```bash
# Ver logs
docker logs pos-backend
docker logs pos-frontend

# Detener todo
docker stop pos-backend pos-frontend

# Limpiar contenedores
docker rm pos-backend pos-frontend
```
