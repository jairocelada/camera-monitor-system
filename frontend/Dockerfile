FROM node:24.14.0-alpine

WORKDIR /app

# Copiar package.json primero (cache)
COPY package*.json ./

RUN npm ci

# Copiar código
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]