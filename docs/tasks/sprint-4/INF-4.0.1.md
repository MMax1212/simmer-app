---
id: INF-4.0.1
story: INF-4.0
sprint: 4
assignee: John Weaver
estimate_hours: 4
---

# Build Multi-Stage Production Dockerfile Container Configurations

## Description
Serves **INF-4.0** (*Production Staging Deployment*). As Simmer approaches its v1.0 release, reliable and reproducible deployments require containerized environments for both the FastAPI backend and Vite React frontend.

This task creates optimized, multi-stage production container configurations (`Dockerfile`) and container ignore files (`.dockerignore`) for both sub-projects, along with a staging container orchestration definition (`docker-compose.staging.yml`) and Nginx production web server reverse proxy configuration (`frontend/nginx.conf`).

Multi-stage builds decouple build-time dependencies (compilers, Node.js toolchains, development libraries) from the final runtime images. This drastically reduces image sizes, eliminates security vulnerabilities associated with development tools in production, and enforces least-privilege security by executing containers under non-root users.

## Specs
- **Backend Multi-Stage Container (`backend/Dockerfile`):**
  - **Stage 1 (Builder):** Uses official `python:3.12-slim` image. Installs OS build essentials if required, sets up an isolated Python virtual environment in `/opt/venv`, and installs dependencies from `requirements.txt` with wheel caching.
  - **Stage 2 (Runtime):** Uses a clean `python:3.12-slim` base image. Copies the populated `/opt/venv` from the builder stage. Copies backend application code (`app/`, `migrations/`, `alembic.ini`).
  - **Security & User:** Creates a non-root system group and user (`simmeruser`, UID/GID 1001) and switches execution context via `USER simmeruser`.
  - **Environment & Execution:** Sets `PYTHONUNBUFFERED=1`, `PYTHONDONTWRITEBYTECODE=1`, and prepends `/opt/venv/bin` to `PATH`. Exposes container port `8000`. Defines `HEALTHCHECK` verifying endpoint responsiveness. Sets `CMD` to launch `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
  - **`.dockerignore` (`backend/.dockerignore`):** Excludes `.venv`, `__pycache__`, `.pytest_cache`, `.git`, `.env`, SQLite database files (`*.db`), and test artifacts.

- **Frontend Multi-Stage Container (`frontend/Dockerfile`):**
  - **Stage 1 (Builder):** Uses official `node:22-alpine` image. Copies `package.json` and `package-lock.json`, executes `npm ci` for deterministic dependency resolution, copies source files, and builds static production assets via `npm run build` targeting `/app/dist`.
  - **Stage 2 (Runtime):** Uses lightweight `nginx:1.27-alpine` web server image. Copies production Nginx virtual host configuration (`nginx.conf`) supporting client-side SPA routing (`try_files $uri $uri/ /index.html;`) and reverse-proxying `/api/` requests to the backend service. Copies compiled assets from builder `/app/dist` to `/usr/share/nginx/html`.
  - **Security & User:** Runs as standard Nginx unprivileged or configured user, exposes port `80`, and sets up healthcheck directives.
  - **`.dockerignore` (`frontend/.dockerignore`):** Excludes `node_modules`, `dist`, `.git`, test artifacts, and IDE metadata.

- **Staging Orchestration Configuration (`docker-compose.staging.yml`):**
  - Defines `backend` service building from `./backend/Dockerfile` with exposed port `8000`, environment variables, and healthcheck.
  - Defines `frontend` service building from `./frontend/Dockerfile` with exposed port `80` (mapped to host `80` or `3000`), depending on backend service health.
  - Configures an internal container network (`simmer-staging-network`) for secure inter-service communication.

## Requirements
- Adhere to Docker and Open Container Initiative (OCI) best practices for caching layers and minimal attack surface.
- Strictly enforce multi-stage builds separating build tools from production execution.
- Never run containers as root user in production runtime stages.
- Maintain comprehensive, beginner-friendly comments throughout every Dockerfile, Nginx config, and compose file explaining each directive and its architectural rationale.
- Add dedicated automated structural and validation tests in `backend/tests/test_INF_4_0_1.py`.
- Ensure all existing backend tests continue to pass with zero regressions.

## Acceptance criteria
1. `backend/Dockerfile` defines a valid multi-stage build (`builder` and `runtime` stages) based on Python 3.12, sets up an isolated virtual environment, creates and switches to non-root user `simmeruser`, sets `PYTHONUNBUFFERED=1`, exposes port 8000, and defines an HTTP healthcheck.
2. `backend/.dockerignore` exists and excludes cache directories (`__pycache__`, `.pytest_cache`), local virtual environments (`.venv`), git metadata, and local database files (`*.db`).
3. `frontend/Dockerfile` defines a valid multi-stage build using Node 22 for building assets and Nginx Alpine for serving static assets, copies compiled artifacts to `/usr/share/nginx/html`, exposes port 80, and specifies a healthcheck.
4. `frontend/nginx.conf` exists and provides SPA HTML5 history routing (`try_files $uri $uri/ /index.html`) and forwards `/api/` traffic to the backend container.
5. `frontend/.dockerignore` exists and excludes `node_modules`, build output `dist`, and test cache files.
6. `docker-compose.staging.yml` defines both `backend` and `frontend` services connected via a dedicated bridge network with appropriate environment variable bindings and healthcheck dependencies.
7. Automated tests in `backend/tests/test_INF_4_0_1.py` validate the presence, syntax, multi-stage structure, security directives, and configuration integrity of all containerization files.
