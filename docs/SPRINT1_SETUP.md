# Sprint 1 setup (auth, profiles, recipes, admin)

## 1. Copy the files in
Copy `backend/` and `frontend/` over your repo's folders of the same name.
These existing files get replaced: `backend/app/main.py`, `backend/requirements.txt`,
`frontend/src/App.tsx`, `frontend/src/main.tsx`. Your `index.html` and `package.json` are not touched.
If the Vite template left `App.css` / `index.css` in `frontend/src`, you can delete them; styles now live in `src/styles.css`.

Add these lines to `.gitignore` if they aren't there:
```
*.db
.env
```

## 2. Backend
```bash
cd backend
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt    # new packages: sqlalchemy, PyJWT, bcrypt, pydantic-settings, ...
cp .env.example .env               # then change SECRET_KEY to a long random string
pytest                             # 15 tests should pass
uvicorn app.main:app --reload --port 8000
```
`simmer.db` is created automatically the first time the server starts.

Make yourself an admin (register in the app first):
```bash
python -m app.make_admin you@example.com
```

To test protected endpoints in Swagger (http://localhost:8000/docs), click **Authorize** and put your **email** in the "username" box.

## 3. Frontend
```bash
cd frontend
npm install react-router-dom
npm run dev
```
Open http://localhost:5173, sign up, and you'll land on your profile page.

## Which files belong to which story
| Story | Backend | Frontend |
|---|---|---|
| US1.1 Register / log in | `api/auth.py`, `core/security.py`, `models/user.py` | `pages/Register.tsx`, `pages/Login.tsx`, `context/` |
| US1.2 Admin role + panel | `api/admin.py`, `require_admin` in `api/deps.py`, `make_admin.py` | `pages/Admin.tsx` |
| US1.3 Edit profile | `PATCH /api/users/me` in `api/users.py` | `pages/Profile.tsx` |
| US1.4 Create/save recipes | `api/recipes.py`, `models/recipe.py` | `pages/RecipeForm.tsx`, `pages/RecipeDetail.tsx` |
| US1.5 My Recipes tab | `GET /api/users/me/recipes` | `pages/MyRecipes.tsx` |

## Endpoints
| Method | Path | Who can call it |
|---|---|---|
| POST | /api/auth/register | anyone |
| POST | /api/auth/login | anyone |
| GET / PATCH | /api/users/me | logged-in user |
| GET | /api/users/me/recipes | logged-in user |
| GET | /api/users/{username} | anyone |
| POST | /api/recipes | logged-in user |
| GET | /api/recipes/{id} | anyone |
| PUT / DELETE | /api/recipes/{id} | recipe owner or admin |
| GET | /api/admin/users | admin |
| PATCH | /api/admin/users/{id} | admin |

## Decisions the team should know about
- Ingredients are already structured rows (name, quantity, unit), so US2.4 and the Sprint 4 grocery list need no data migration.
- `DietaryPref` in `schemas/user.py` is the single shared tag list. Reuse it for recipe tags in US4.4.
- Avatars are a URL for now. Real image upload should be a Sprint 3 spike, since post photos need it too.
- Tables are created on startup with `create_all`. Before Sprint 2 changes the models, set up Alembic;
  until then, anyone who pulls a model change has to delete their `simmer.db`.
- The login token is stored in localStorage. It's simple, but any script on the page can read it; that's acceptable for this project.
- The placeholder endpoint `/api/recipes/placeholder` was removed.
