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
uvicorn app.main:app --reload --port 8000
```
- Interactive API Docs will be available at: [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Run the Frontend (TypeScript / React)
In terminal window #2:
```bash
cd frontend
npm install
npm run dev
```
- Web Application will be live at: [http://localhost:5173](http://localhost:5173)

### 4. Run with Docker Compose
You can run PostgreSQL, FastAPI, and React together with Docker:

**Production Mode:**
```bash
docker compose up --build
```
- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

**Development Mode (Live Code Reload):**
```bash
docker compose -f docker-compose.dev.yml up --build
```
- Frontend (Vite HMR): [http://localhost:5173](http://localhost:5173)
- Backend (FastAPI reload): [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 👥 Team Simmer Roles
- **Maximo Mora** — Product Owner (PO), Full-Stack Developer
- **Bryan Moreno** — Scrum Master, Full-Stack Developer
- **Ulises Diaz** — Full-Stack Developer
- **John Weaver** — Full-Stack Developer
- **Benjamin Ong** — Full-Stack Developer
