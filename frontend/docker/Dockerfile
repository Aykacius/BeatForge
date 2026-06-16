FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application
COPY . .

# Build Next.js app
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
