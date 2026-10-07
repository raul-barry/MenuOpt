# =======================================================
# ETAPA 1: Construcción de la aplicación Angular
# =======================================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copiar manifiesto de dependencias e instalar
COPY package*.json ./
RUN npm install

# Copiar código fuente y compilar para producción
COPY . .
RUN npm run build

# =======================================================
# ETAPA 2: Servidor Web Nginx de alto rendimiento
# =======================================================
FROM nginx:alpine

# Copiar configuración personalizada de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Limpiar directorio html por defecto
RUN rm -rf /usr/share/nginx/html/*

# Copiar archivos compilados de Angular
COPY --from=builder /app/dist/menuopt-frontend/browser/ /usr/share/nginx/html/

# Puerto estándar para el frontend de MenuOpt
EXPOSE 4200

CMD ["nginx", "-g", "daemon off;"]
