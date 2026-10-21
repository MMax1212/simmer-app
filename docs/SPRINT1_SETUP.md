# Sprint 1 setup

The acceptance contract is in [spec.md](spec.md) and [intent.md](intent.md).
Use Python 3.11+ and Node.js 24. Docker is optional and is not required for these checks.

## Backend and database

From the repository root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set SECRET_KEY in .env to a long random value before sharing/deploying.
alembic upgrade head
python -m pytest -q
uvicorn app.main:app --reload --port 8000
```

On Windows, activate with `.venv\Scripts\activate`.

Run `alembic upgrade head` for new databases AND databases created by John's original
Sprint 1 code. Back up an existing database before upgrading, with the server stopped.
Do not delete it or run `alembic stamp head`: the upgrade converts its data.
The API no longer creates tables at startup.

Migration 0001 creates or recognizes the original tables. Migration 0002 preserves
user/recipe/ingredient IDs and passwords, renames the contract fields, converts each
nonblank instruction line to an ordered step (preserving text), fills missing timings
and servings with their documented defaults, repairs null preference lists, and adds
recipe metadata and admin audit records. Existing bcrypt passwords remain usable and
are upgraded to Argon2 after successful login.

Unknown legacy ingredient amounts/units remain null rather than being fabricated.
Legacy recipes remain readable; complete their missing ingredients/steps before saving
an edit under the new validation rules. The migration is forward-only: to roll back,
restore the pre-upgrade database backup and use the prior application version.

All developers have their own local SQLite database. Tests use isolated databases.

Promote an existing registered account:

```bash
python -m app.make_admin you@example.com
```

Log in again to refresh the UI's role. Admin status/role changes are recorded in
`admin_audit`. Admins cannot change their own account from the management panel.

## Frontend

In a second terminal:

```bash
cd frontend
npm ci
npm run dev
```

Open http://localhost:5173. Vite proxies relative API requests to port 8000.
For another API origin, set `VITE_API_URL` before building. Configure the backend
`CORS_ORIGINS` as a JSON array of allowed frontend origins when using separate hosts.

## Checks

```bash
# In backend/, with its virtual environment active:
python -m pytest -q

# In frontend/:
npm test
npm run build
npx playwright install chromium
npm run test:e2e
```

For browser tests, make sure `python` on PATH is the backend virtual environment's
Python, or set `E2E_PYTHON` to its absolute executable path. The test runner starts
dedicated servers on ports 8001 and 5174, uses a temporary migrated database, and
refuses to reuse a running server. It does not touch `simmer.db`.

GitHub Actions runs backend tests, frontend tests/build, and Chromium integration tests.
A repository admin must make those checks required in branch rules to block failed merges.

## API contract

| Method | Path | Access |
|---|---|---|
| POST | /api/v1/auth/register | Anyone |
| POST | /api/v1/auth/login | Anyone; username_or_email and password |
| GET | /api/v1/auth/me | Signed-in user |
| PUT | /api/v1/users/me | Signed-in user |
| GET | /api/v1/users/{username} | Public profile without email/role |
| GET | /api/v1/recipes/my-recipes?offset=0&limit=20 | Signed-in user |
| POST | /api/v1/recipes | Signed-in user |
| GET | /api/v1/recipes/{id} | Anyone |
| PUT / DELETE | /api/v1/recipes/{id} | Author or admin |
| GET | /api/v1/admin/users | Admin |
| PATCH | /api/v1/admin/users/{id}/status | Admin |
| GET | /api/health | Anyone |

Login returns a bearer token and the signed-in user's profile. Request schemas reject
unknown fields rather than silently dropping them. Passwords/request bodies are never
echoed in validation responses. User-supplied avatar and recipe image URLs must use HTTP(S).
