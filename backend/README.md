# Simmer Backend (FastAPI + Python)

## Prerequisites
- Python 3.10 or higher
- `pip` package manager

## Local Setup

1. Open your terminal in this `backend/` directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment (isolates your packages from system Python):
   ```bash
   python3 -m venv .venv
   ```

3. Activate the virtual environment:
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows (PowerShell):
     ```powershell
     .venv\Scripts\Activate.ps1
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the development server with live reload:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

6. Open the interactive Swagger API documentation in your browser:
   - **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
   - **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
