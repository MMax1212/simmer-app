# Local account and admin experiment

This checkout implements only US1.1 and US1.2. The full sprint requirements are
retained in the planning documents for reference.

Use Python 3.11+ and Node.js 24. This experiment uses a separate fresh accounts.db;
existing full-sprint databases have not been changed. The simplified migration
history in this checkout is intended for a fresh database, not for upgrading an
existing full-sprint database.

## Backend

From backend/:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Set DATABASE_URL to sqlite:///./accounts.db if an existing .env points to simmer.db.
Set SECRET_KEY to a long random value before sharing the application.

To promote a registered account, run:

```bash
python -m app.make_admin you@example.com
```

## Frontend

From frontend/:

```bash
npm ci
npm run dev
```

Open http://localhost:5173. Registration and login lead to the home screen.
Administrators can open the user-management screen.

## Checks

Run python -m pytest -q from backend/ and npm test plus npm run build from frontend/.

For browser checks, activate the backend Python environment, then run
npx playwright install chromium and npm run test:e2e from frontend/.
Alternatively, set E2E_PYTHON to the backend Python executable's absolute path.
Browser checks use temporary databases and dedicated servers.

## Endpoints

| Method | Path |
|---|---|
| POST | /api/v1/auth/register |
| POST | /api/v1/auth/login |
| GET | /api/v1/auth/me |
| POST | /api/v1/auth/token |
| GET | /api/v1/admin/users |
| PATCH | /api/v1/admin/users/{id}/status |
| GET | /api/health |
