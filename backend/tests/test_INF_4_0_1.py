"""
test_INF_4_0_1.py — Automated Verification for Task INF-4.0.1
================================================================================
Task ID: INF-4.0.1
Story:   INF-4.0 (Production Staging Deployment)
Author:  John Weaver

This test suite validates the architectural integrity, multi-stage structure,
security hardening, and configuration parameters of the containerization
infrastructure created for production staging deployment:
  1. Backend Multi-Stage Dockerfile (python:3.12, non-root user, venv isolation, healthcheck)
  2. Backend .dockerignore (cache, virtualenvs, sqlite databases, git metadata)
  3. Frontend Multi-Stage Dockerfile (node:22 build stage, nginx:1.27 runtime stage)
  4. Frontend Nginx configuration (SPA routing fallback, /api/ reverse proxy, gzip, healthz)
  5. Frontend .dockerignore (node_modules, dist, test artifacts)
  6. Staging Docker Compose Manifest (services, bridge network, healthcheck dependency)
  7. Backend /api/health endpoint responsiveness (target for container healthcheck)
================================================================================
"""

from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app

# Resolve paths to project root, backend, and frontend
BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_DIR.parent
FRONTEND_DIR = REPO_ROOT / "frontend"


def test_INF_4_0_1_backend_dockerfile_multistage():
    """
    Acceptance Criterion 1:
    backend/Dockerfile must implement a multi-stage build (builder + runtime),
    use Python 3.12, isolate dependencies in a virtual environment, create
    and switch to a non-root user (simmeruser), set PYTHONUNBUFFERED=1,
    expose port 8000, and define an HTTP healthcheck.
    """
    dockerfile_path = BACKEND_DIR / "Dockerfile"
    assert dockerfile_path.exists(), "backend/Dockerfile must exist"

    content = dockerfile_path.read_text()

    # Stage 1: Builder validation
    assert "FROM python:3.12-slim AS builder" in content, "Must use python:3.12-slim builder stage"
    assert "/opt/venv" in content, "Must isolate dependencies inside a virtual environment"
    assert "pip install" in content, "Must install requirements in builder stage"

    # Stage 2: Runtime validation
    assert "FROM python:3.12-slim AS runtime" in content, "Must use python:3.12-slim runtime stage"
    assert "COPY --from=builder /opt/venv /opt/venv" in content, "Must copy venv from builder stage"

    # Security: Non-root user execution (CIS benchmark)
    assert "useradd" in content and "simmeruser" in content, "Must create dedicated non-root user simmeruser"
    assert "USER simmeruser" in content, "Must switch execution context to non-root user"

    # Environment & Networking
    assert "PYTHONUNBUFFERED=1" in content, "Must set PYTHONUNBUFFERED=1 for immediate log flushing"
    assert "EXPOSE 8000" in content, "Must expose container port 8000"

    # Healthcheck
    assert "HEALTHCHECK" in content, "Must declare a HEALTHCHECK instruction"
    assert "/api/health" in content, "Healthcheck should probe the /api/health endpoint"


def test_INF_4_0_1_backend_dockerignore():
    """
    Acceptance Criterion 2:
    backend/.dockerignore must exclude heavy local caches, local venvs,
    temporary sqlite databases, and git metadata from build contexts.
    """
    dockerignore_path = BACKEND_DIR / ".dockerignore"
    assert dockerignore_path.exists(), "backend/.dockerignore must exist"

    content = dockerignore_path.read_text()
    assert "__pycache__" in content, "Must ignore __pycache__"
    assert ".venv" in content, "Must ignore local .venv"
    assert ".pytest_cache" in content, "Must ignore .pytest_cache"
    assert ".git" in content, "Must ignore .git metadata"
    assert "*.db" in content, "Must ignore local SQLite database files"


def test_INF_4_0_1_frontend_dockerfile_multistage():
    """
    Acceptance Criterion 3:
    frontend/Dockerfile must implement a multi-stage build with Node 22 builder
    and Nginx Alpine runtime, copy compiled assets to /usr/share/nginx/html,
    expose port 80, and declare a healthcheck.
    """
    dockerfile_path = FRONTEND_DIR / "Dockerfile"
    assert dockerfile_path.exists(), "frontend/Dockerfile must exist"

    content = dockerfile_path.read_text()

    # Stage 1: Node builder
    assert "FROM node:22-alpine AS builder" in content, "Must use node:22-alpine builder stage"
    assert "npm ci" in content, "Must use npm ci for deterministic dependency installation"
    assert "npm run build" in content, "Must execute npm run build to compile Vite assets"

    # Stage 2: Nginx runtime
    assert "FROM nginx:1.27-alpine AS runtime" in content, "Must use nginx:1.27-alpine runtime stage"
    assert "COPY --from=builder /app/dist /usr/share/nginx/html" in content, (
        "Must copy compiled assets to Nginx static serving root"
    )
    assert "EXPOSE 80" in content, "Must expose standard HTTP port 80"
    assert "HEALTHCHECK" in content, "Must declare a container HEALTHCHECK instruction"


def test_INF_4_0_1_frontend_nginx_conf():
    """
    Acceptance Criterion 4:
    frontend/nginx.conf must configure client-side SPA routing fallback
    (try_files $uri $uri/ /index.html;), gzip compression, reverse-proxying
    for /api/ traffic, and a healthcheck route.
    """
    nginx_conf_path = FRONTEND_DIR / "nginx.conf"
    assert nginx_conf_path.exists(), "frontend/nginx.conf must exist"

    content = nginx_conf_path.read_text()

    # SPA routing
    assert "try_files $uri $uri/ /index.html;" in content, "Must configure SPA fallback to /index.html"

    # Reverse proxy for API
    assert "location /api/" in content, "Must configure location block for /api/"
    assert "proxy_pass http://backend:8000;" in content, "Must reverse proxy /api/ to backend:8000"

    # Compression and health check
    assert "gzip on;" in content, "Must enable gzip compression for static assets"
    assert "/healthz" in content, "Must declare a lightweight /healthz endpoint"


def test_INF_4_0_1_frontend_dockerignore():
    """
    Acceptance Criterion 5:
    frontend/.dockerignore must exclude node_modules, dist, test results,
    and git metadata from the build context.
    """
    dockerignore_path = FRONTEND_DIR / ".dockerignore"
    assert dockerignore_path.exists(), "frontend/.dockerignore must exist"

    content = dockerignore_path.read_text()
    assert "node_modules/" in content, "Must ignore node_modules/"
    assert "dist/" in content, "Must ignore dist/"
    assert ".git" in content, "Must ignore .git metadata"


def test_INF_4_0_1_docker_compose_staging():
    """
    Acceptance Criterion 6:
    docker-compose.staging.yml must define both backend and frontend services,
    connect them via a dedicated bridge network, specify healthcheck dependencies,
    and configure persistent data storage.
    """
    compose_path = REPO_ROOT / "docker-compose.staging.yml"
    assert compose_path.exists(), "docker-compose.staging.yml must exist"

    content = compose_path.read_text()

    # Services
    assert "backend:" in content, "Must define backend service"
    assert "frontend:" in content, "Must define frontend service"

    # Healthcheck dependency
    assert "condition: service_healthy" in content, "Frontend must depend on backend being healthy"

    # Network topology
    assert "simmer-staging-network" in content, "Must define and connect to simmer-staging-network"


def test_INF_4_0_1_backend_api_health_endpoint():
    """
    Acceptance Criterion 7:
    The backend /api/health endpoint targeted by the container HEALTHCHECK
    must return HTTP 200 OK with status='ok'.
    """
    client = TestClient(app)
    response = client.get("/api/health")

    assert response.status_code == 200, "Health check endpoint must return HTTP 200"
    data = response.json()
    assert data.get("status") == "ok", "Health check status must be 'ok'"
