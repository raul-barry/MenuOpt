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

# La configuración se procesa al iniciar para conectar con la API privada de Render.
COPY nginx.conf /etc/nginx/templates/default.conf.template
ENV NGINX_ENVSUBST_FILTER="^(API_HOST|API_PORT)$"

# Limpiar directorio html por defecto
RUN rm -rf /usr/share/nginx/html/*

# Copiar archivos compilados de Angular
COPY --from=builder /app/dist/menuopt-frontend/browser/ /usr/share/nginx/html/

# Puerto HTTP esperado por Render
EXPOSE 10000

CMD ["nginx", "-g", "daemon off;"]
