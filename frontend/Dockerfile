# Etapa de construcción
FROM node:20-alpine AS builder

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm install --only=production --legacy-peer-deps

# Copiar código fuente
COPY . .

# Construir la aplicación
RUN npm run build

# Etapa de producción con nginx
FROM nginx:alpine

# Copiar archivos construidos
COPY --from=builder /app/build /usr/share/nginx/html

# Copiar configuración de nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Exponer puerto 80
EXPOSE 80

# Comando por defecto
CMD ["nginx", "-g", "daemon off;"]
