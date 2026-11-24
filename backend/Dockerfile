# ==============================================================================
# Simmer Backend Multi-Stage Production Dockerfile
# ==============================================================================
# Architectural Overview:
# Multi-stage builds separate the compile-time/build-time tools (compilers, headers,
# package managers) from the final execution environment.
#
# Benefits:
# 1. Minimal Image Size: Build-time packages and build caches are discarded.
# 2. Hardened Security: No gcc/make or dev dependencies left in the final image.
# 3. Least Privilege: Executes under an unprivileged non-root user (simmeruser).
# 4. Layer Caching: Requirements installation is isolated so code edits build fast.
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Build Environment (Builder)
# ------------------------------------------------------------------------------
# We use Python 3.12 slim as the base to keep download sizes small while providing
# a stable Debian-based environment for compiling any native Python wheels.
FROM python:3.12-slim AS builder

# Prevent Python from writing .pyc files to disk and ensure output is printed immediately
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set the working directory for dependency preparation
WORKDIR /build

# Install OS dependencies needed for compiling wheels (e.g., greenlet, bcrypt, psycopg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create an isolated virtual environment at /opt/venv
# Installing packages into a standalone venv directory makes it trivial to copy
# the entire package tree cleanly into Stage 2 (the runtime image).
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy ONLY requirements.txt first.
# Docker caches this layer: as long as requirements.txt has not changed,
# subsequent builds will reuse the cached dependencies instantly.
COPY requirements.txt .

# Install production dependencies into our virtual environment
RUN pip install --upgrade pip && \
    pip install -r requirements.txt


# ------------------------------------------------------------------------------
# Stage 2: Final Production Runtime (Runner)
# ------------------------------------------------------------------------------
# Start fresh from a clean python:3.12-slim image without the build-essential tools.
FROM python:3.12-slim AS runtime

# Python environment settings for production execution:
# - PYTHONUNBUFFERED=1: Flushes stdout and stderr immediately so logs appear in real-time
# - PYTHONDONTWRITEBYTECODE=1: Avoids generating .pyc bytecode files inside container
# - PATH: Points directly to the virtual environment binary directory
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000

# Install lightweight runtime utilities (e.g. curl for container health checking)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Security Hardening: Never run production web services as the 'root' superuser.
# We create a dedicated system group and user with explicit UID and GID (1001).
RUN groupadd -g 1001 simmergroup && \
    useradd -u 1001 -g simmergroup -s /bin/bash -m simmeruser

# Copy the pre-built virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Set the application root working directory
WORKDIR /app

# Copy application source code and migrations into the container
COPY --chown=simmeruser:simmergroup app /app/app
COPY --chown=simmeruser:simmergroup migrations /app/migrations
COPY --chown=simmeruser:simmergroup alembic.ini /app/alembic.ini

# Drop privileges by switching to our unprivileged user
USER simmeruser

# Document that the container listens on port 8000
EXPOSE 8000

# Container Healthcheck:
# Periodically probes the backend API health endpoint to confirm the server is responsive.
# If 3 consecutive checks fail, Docker or the orchestrator marks the container UNHEALTHY.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start the FastAPI application via Uvicorn server in production mode
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
