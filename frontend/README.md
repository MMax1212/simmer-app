# Simmer Frontend (React + TypeScript + Vite)

## Prerequisites
- Node.js (v18.0.0 or higher recommended)
- `npm` package manager

## Local Setup

1. Open your terminal in this `frontend/` directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
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
