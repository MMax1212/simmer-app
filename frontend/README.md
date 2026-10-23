# Simmer Frontend (React + TypeScript + Vite)

## Prerequisites
- Node.js 24 recommended (minimum 22.12)
- `npm` package manager

## Local Setup

1. Open your terminal in this `frontend/` directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm ci
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser at:
   - [http://localhost:5173](http://localhost:5173)

## How the Frontend talks to the Backend
During development, Vite automatically forwards any requests starting with `/api` to the Python backend running on `http://localhost:8000` (configured in `vite.config.ts`).
This means you do not have to worry about CORS errors when testing locally!

Run `npm test` for frontend tests and `npm run build` for TypeScript/build checks.
See [Sprint 1 setup](../docs/SPRINT1_SETUP.md) for Playwright browser tests.
