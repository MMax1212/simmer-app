# ==============================================================================
# Simmer Frontend Multi-Stage Production Dockerfile
# ==============================================================================
# Architectural Overview:
# 1. Stage 1 (Builder): Uses Node.js 22 to compile TypeScript, process Tailwind CSS,
#    and build the optimized single-page static bundle via Vite.
# 2. Stage 2 (Runner): Discards the heavy Node.js runtime and node_modules entirely,
#    copying only the small static HTML/JS/CSS assets into an ultra-lean Nginx
#    Alpine web server image (~25MB).
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Build Environment (Vite + React + TypeScript)
# ------------------------------------------------------------------------------
FROM node:22-alpine AS builder

WORKDIR /app

# Copy dependency manifests first to leverage Docker layer caching.
# If dependencies haven't changed, Docker reuses the cached node_modules layer.
COPY package.json package-lock.json ./

# Install exact dependency versions cleanly and deterministically
RUN npm ci

# Copy project source files and configuration
COPY tsconfig.json vite.config.ts index.html ./
COPY src/ ./src/

# Compile TypeScript and bundle production assets with Vite
# Output lands in /app/dist
RUN npm run build


# ------------------------------------------------------------------------------
# Stage 2: Production Web Server (Nginx Alpine)
# ------------------------------------------------------------------------------
FROM nginx:1.27-alpine AS runtime

# Remove default boilerplate configuration
RUN rm -f /etc/nginx/conf.d/default.conf

# Copy our tailored SPA Nginx configuration (with gzip, SPA routing, and API reverse proxy)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built static assets from the builder stage into Nginx's serving root
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose standard HTTP port
EXPOSE 80

# Health check to ensure Nginx is actively responding to requests
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q --spider http://localhost/healthz || exit 1

# Launch Nginx in the foreground so the container remains active
CMD ["nginx", "-g", "daemon off;"]
