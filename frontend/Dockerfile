FROM node:24-alpine

WORKDIR /app

# npm ci : installe EXACTEMENT les versions figées dans package-lock.json
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
