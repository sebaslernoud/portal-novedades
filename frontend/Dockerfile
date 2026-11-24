# Imagen de desarrollo: servidor de Vite con recarga en caliente.
# Para producción, `npm run build` genera dist/ (estáticos) para servir detrás del backend o de un servidor web.
FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
# Tolerar redes lentas sin cortar la instalación.
RUN npm install --fetch-timeout=600000 --fetch-retries=5

COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev"]
