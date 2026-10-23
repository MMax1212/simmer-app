# Simmer 🍳 — Cooking Social Media Web Application

Simmer is a social cooking web application where food lovers can discover, author, and organize recipes, connect with fellow home chefs, and share culinary creations.

Developed for **CSE 115a / CMPS 115: Software Engineering & Methodology**.

---

## Local experiment scope

This local checkout implements only US1.1 (accounts/login) and US1.2 (admin management).
Profile and recipe files are retained empty. The full sprint planning documents remain
reference material. Use a fresh `accounts.db`; existing full-sprint databases are unchanged.
See [local setup](docs/SPRINT1_SETUP.md).

## 🛠 Tech Stack

- **Backend:** Python 3.11+, [FastAPI](https://fastapi.tiangolo.com/) (modern, high-performance, auto-generates Swagger API documentation)
- **Frontend:** TypeScript, [React](https://react.dev/), [Vite](https://vitejs.dev/) (fast, component-based UI)
- **Database:** SQLite (development) / PostgreSQL (production), SQLAlchemy ORM
- **Testing:** Pytest (backend), Vitest / React Testing Library (frontend)

---

## 📁 Repository Structure

```
simmer/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── README.md
├── docs/
├── .gitignore
└── README.md
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
source .venv/bin/activate
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

The workflow checks account/admin backend tests, frontend tests and the production
build, plus browser registration/login and session handling. Checks need no Docker
or repository secrets. See [local setup](docs/SPRINT1_SETUP.md) for commands.
