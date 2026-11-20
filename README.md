# Simmer 🍳 — Cooking Social Media Web Application

Simmer is a social cooking web application where food lovers can discover, author, and organize recipes, connect with fellow home chefs, and share culinary creations.

Developed for **CSE 115a / CMPS 115: Software Engineering & Methodology**.

---

## 🛠 Tech Stack

- **Backend:** Python 3.11+, [FastAPI](https://fastapi.tiangolo.com/) (modern, high-performance, auto-generates Swagger API documentation)
- **Frontend:** TypeScript, [React](https://react.dev/), [Vite](https://vitejs.dev/) (fast, component-based UI)
- **Database:** SQLite (development) / PostgreSQL (production), SQLAlchemy ORM
- **Testing:** Pytest (backend), Vitest / React Testing Library (frontend)

---

## 📁 Repository Structure

```
simmer/
├── backend/               # Python API server
│   ├── app/
│   │   ├── api/           # API endpoints (auth, recipes, users)
│   │   ├── core/          # Configuration and security
│   │   ├── models/        # Database models (SQLAlchemy)
│   │   ├── schemas/       # Request/response validation (Pydantic)
│   │   └── main.py        # FastAPI application entry point
│   ├── tests/             # Backend test suite
│   ├── requirements.txt   # Python package dependencies
│   └── README.md          # Backend developer guide
├── frontend/              # TypeScript React application
│   ├── src/
│   │   ├── components/    # Reusable UI widgets (Navbar, Cards, Buttons)
│   │   ├── pages/         # View screens (Home, Login, Profile, Recipes)
│   │   ├── services/      # API client functions
│   │   ├── App.tsx        # Application root component
│   │   └── main.tsx       # Vite entry point
│   ├── package.json       # Node dependencies and scripts
│   └── README.md          # Frontend developer guide
├── docs/                  # Sprint & Release plans, architectural diagrams
├── .gitignore             # Git exclusions (prevents committing venv and node_modules)
└── README.md              # Project documentation (this file)
```

---

## 🚀 Quickstart Guide for Team Members

### 1. Clone the Repository
```bash
git clone https://github.com/MMax1212/simmer-app.git
cd simmer-app
```

### 2. Run the Backend (Python)
In terminal window #1:
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate       # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```
- Interactive API Docs will be available at: [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Run the Frontend (TypeScript / React)
In terminal window #2:
```bash
cd frontend
npm ci
npm run dev
```
- Web Application will be live at: [http://localhost:5173](http://localhost:5173)

---

## 📡 External & Public REST API Endpoints

The Simmer backend exposes a full-featured RESTful API prefixed at `/api/v1`. Interactive OpenAPI documentation is automatically served at [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI) and [http://localhost:8000/redoc](http://localhost:8000/redoc) (ReDoc).

For full payload schemas, query parameters, and JSON response examples, see the [**Complete API Specification Document**](docs/API_README.md).

| Method | Endpoint | Auth Required | Description |
| :--- | :--- | :---: | :--- |
| `POST` | `/api/v1/auth/register` | None (Public) | Register new user account with email, username, and password |
| `POST` | `/api/v1/auth/login` | None (Public) | Authenticate credentials; returns Bearer JWT and user profile |
| `GET`  | `/api/v1/auth/me` | Bearer Token | Retrieve currently authenticated user identity and role |
| `PUT`  | `/api/v1/users/me` | Bearer Token | Update profile (bio, avatar URL, culinary preferences) |
| `GET`  | `/api/v1/users/me/cooking-history` | Bearer Token | Retrieve personal completed recipes cooking log |
| `GET`  | `/api/v1/users/{username}` | None (Public) | Public chef profile lookup |
| `GET`  | `/api/v1/recipes` | None (Public) | Search recipes by keyword (`q`), dietary tags (`tag`), cuisine, and difficulty |
| `POST` | `/api/v1/recipes` | Bearer Token | Author a new structured recipe with ingredients, tools, and steps |
| `GET`  | `/api/v1/recipes/my-recipes` | Bearer Token | List all recipes authored by the authenticated user with pagination |
| `GET`  | `/api/v1/recipes/{id}` | None (Public) | Read full recipe details |
| `PUT`  | `/api/v1/recipes/{id}` | Bearer Token (Author) | Update an authored recipe |
| `DELETE`| `/api/v1/recipes/{id}` | Bearer Token (Author/Admin) | Delete a recipe and cascade child rows |
| `POST` | `/api/v1/recipes/{id}/complete` | Bearer Token | Log recipe as cooked with optional rating (1–5) and notes |
| `POST` | `/api/v1/posts/{id}/like` | Bearer Token | Toggle like status on a community dish post |
| `GET`  | `/api/v1/posts/{id}/comments` | None (Public) | Retrieve list of discussion comments for a post |
| `POST` | `/api/v1/posts/{id}/comments` | Bearer Token | Post a discussion comment under a post (1–1,000 characters) |
| `GET`  | `/api/v1/admin/users` | Bearer Token (Admin) | List registered users with optional role/active filters |
| `PATCH`| `/api/v1/admin/users/{id}/status` | Bearer Token (Admin) | Deactivate/reactivate accounts or toggle roles (with audit logging) |
| `GET`  | `/api/v1/admin/audit-logs` | Bearer Token (Admin) | Retrieve paginated administrative audit logs |
| `GET`  | `/api/v1/admin/stats` | Bearer Token (Admin) | Retrieve system metrics (users, active counts, recipes) |
| `GET`  | `/api/health` | None (Public) | Backend service health check |

---

## 👥 Team Simmer Roles
- **Maximo Mora** — Product Owner (PO), Full-Stack Developer
- **Bryan Moreno** — Scrum Master, Full-Stack Developer
- **Ulises Diaz** — Full-Stack Developer
- **John Weaver** — Full-Stack Developer
- **Benjamin Ong** — Full-Stack Developer

---

## Continuous Integration

GitHub Actions runs the `CI` workflow on every push and pull request. It can also
be started manually from the repository's **Actions** tab once the workflow is
on the default branch.

- **Backend tests:** installs `backend/requirements.txt` with Python 3.11 and
  runs `python -m pytest -q` from `backend/`. Tests use an isolated in-memory
  SQLite database; no Docker, PostgreSQL server, or repository secrets are needed.
- **Frontend tests and build:** installs the committed lockfile with `npm ci` using
  Node.js 24, then runs `npm run build` from `frontend/`. This checks TypeScript
  and creates the production build. Vitest also checks the frontend forms, routing, session expiry, and recipe views.
- **Browser integration tests:** Playwright starts the real API and website against
  a temporary migrated SQLite database and tests onboarding and recipe management.

To run the same checks locally, install the dependencies above, then run:

```bash
cd backend
python -m pytest -q
```

```bash
cd frontend
npm ci
npm test
npm run build
```

Open a pull request's **Checks** tab to see each job and any failure details.
The workflow does not deploy the application. To block merging when checks fail,
a repository administrator must configure the `Backend tests` and
`Frontend tests and build` and `Browser integration tests` checks as required in the branch rules for `main`.

See [Sprint 1 setup](docs/SPRINT1_SETUP.md) for database migration, browser tests, and admin instructions, and [acceptance coverage](docs/SPRINT1_STATUS.md) for requirements and tests.
