# Multi-stage build for production optimization (root-level)
FROM node:22-alpine AS base

# Install dependencies only when needed
FROM base AS deps
# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
RUN apk add --no-cache libc6-compat
WORKDIR /app/frontend

# Install dependencies based on the preferred package manager
COPY frontend/package.json frontend/package-lock.json* ./
# Install full dependencies (dev + prod) to support building with Vite/Rollup
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app/frontend
COPY --from=deps /app/frontend/node_modules ./node_modules
COPY frontend/. .

# Build the application
ENV NODE_ENV=production
RUN npm run build

# Production image, copy all the files and run nginx
FROM nginx:alpine AS runner
WORKDIR /app

# Copy the built application
COPY --from=builder /app/frontend/dist /usr/share/nginx/html

# Copy nginx configuration from repo root
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]


