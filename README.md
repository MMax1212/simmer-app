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
git clone https://github.com/YOUR_TEAM_OR_ORG/simmer.git
cd simmer
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
