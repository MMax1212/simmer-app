# Technical Specification: Simmer Sprint 1 Core Platform

**Feature / Milestone:** Sprint 1 — Foundational Platform, Auth, Profiles & Personal Recipe Library  
**Status:** Approved  
**Date:** 2026-10-12  
**Related Documents:** [intent.md](./intent.md), [Sprint_Plan_1.md](./Sprint_Plan_1.md), [Architecture_Design.md](./Architecture_Design.md)

---

## 1. Scope & System Overview

This specification details the technical contracts, schemas, and verification rules for Sprint 1 of Simmer.
All implementations must adhere to the three-tier architecture:
- **Presentation Tier:** React 18, TypeScript, Tailwind CSS, Vite (`frontend/src/`)
- **Application Tier:** FastAPI (Python 3.11+), Pydantic v2, Pytest (`backend/app/`)
- **Persistence Tier:** SQLAlchemy 2.0 ORM with SQLite for local development (`backend/simmer.db`)

---

## 2. Database Schema & Data Models

### 2.1 Table: `users`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key, Autoincrement | Unique user identifier |
| `username` | String(50) | Unique, Not Null, Index | User handle |
| `email` | String(100) | Unique, Not Null, Index | User email address |
| `hashed_password` | String(255) | Not Null | Bcrypt hashed password |
| `role` | String(20) | Not Null, Default: `"user"` | Role: `"user"` or `"admin"` |
| `bio` | Text | Nullable | User biography/summary |
| `avatar_url` | String(255) | Nullable | URL to user profile avatar |
| `culinary_preferences` | JSON / Text | Nullable, Default: `[]` | List of culinary tag strings |
| `is_active` | Boolean | Not Null, Default: `True` | Account active status (admin switchable) |
| `created_at` | DateTime | Not Null, Default: `UTC now` | Timestamp of account creation |

### 2.2 Table: `recipes`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key, Autoincrement | Unique recipe identifier |
| `author_id` | Integer | Foreign Key (`users.id`), Not Null | Author user ID |
| `title` | String(150) | Not Null, Index | Title of the recipe |
| `description` | Text | Nullable | Brief summary of the dish |
| `cuisine` | String(50) | Nullable | E.g., Italian, Mexican |
| `meal_type` | String(50) | Nullable | E.g., Breakfast, Dinner |
| `prep_time_mins` | Integer | Not Null, Default: `0` | Preparation time in minutes |
| `cook_time_mins` | Integer | Not Null, Default: `0` | Cooking time in minutes |
| `servings` | Integer | Not Null, Default: `1` | Number of servings |
| `difficulty` | String(20) | Default: `"medium"` | `"easy"`, `"medium"`, `"hard"` |
| `image_url` | String(255) | Nullable | Preview image URL |
| `created_at` | DateTime | Not Null, Default: `UTC now` | Creation timestamp |

### 2.3 Table: `recipe_ingredients`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key, Autoincrement | Ingredient entry ID |
| `recipe_id` | Integer | Foreign Key (`recipes.id`, ondelete: CASCADE), Not Null | Associated recipe |
| `name` | String(100) | Not Null | Ingredient name (e.g., "Olive Oil") |
| `amount` | Float | Not Null | Numeric quantity (e.g., `2.5`) |
| `unit` | String(30) | Not Null | Unit (e.g., "tbsp", "cups", "grams") |

### 2.4 Table: `recipe_steps`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key, Autoincrement | Instruction step ID |
| `recipe_id` | Integer | Foreign Key (`recipes.id`, ondelete: CASCADE), Not Null | Associated recipe |
| `step_number` | Integer | Not Null | 1-indexed execution order |
| `instruction` | Text | Not Null | Detailed step instruction |

---

## 3. Pydantic Schemas (Data Transfer Objects)

```python
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLoginRequest(BaseModel):
    username_or_email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserPublicResponse"

class UserPublicResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    culinary_preferences: List[str] = []
    created_at: datetime

class UserProfileUpdateRequest(BaseModel):
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    culinary_preferences: Optional[List[str]] = None

class IngredientDTO(BaseModel):
    name: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1)

class RecipeStepDTO(BaseModel):
    step_number: int = Field(..., ge=1)
    instruction: str = Field(..., min_length=3)

class RecipeCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    description: Optional[str] = None
    cuisine: Optional[str] = None
    meal_type: Optional[str] = None
    prep_time_mins: int = Field(default=0, ge=0)
    cook_time_mins: int = Field(default=0, ge=0)
    servings: int = Field(default=1, ge=1)
    difficulty: Optional[str] = "medium"
    image_url: Optional[str] = None
    ingredients: List[IngredientDTO] = Field(..., min_items=1)
    steps: List[RecipeStepDTO] = Field(..., min_items=1)

class RecipeDetailResponse(RecipeCreateRequest):
    id: int
    author_id: int
    created_at: datetime
```

---

## 4. API Endpoints Contract

### 4.1 Authentication & Profile (`/api/v1/auth`, `/api/v1/users`)

| Method | Path | Auth Required | Description | Responses |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | None | Register new user account | `201 Created`, `400 Bad Request`, `409 Conflict` (duplicate username/email) |
| `POST` | `/api/v1/auth/login` | None | Authenticate with credentials | `200 OK` (TokenResponse), `401 Unauthorized` |
| `GET` | `/api/v1/auth/me` | Bearer Token | Fetch current authenticated user | `200 OK` (UserPublicResponse), `401 Unauthorized` |
| `PUT` | `/api/v1/users/me` | Bearer Token | Update user bio, avatar, preferences | `200 OK` (UserPublicResponse), `400 Bad Request` |

### 4.2 Administration (`/api/v1/admin`)

| Method | Path | Auth Required | Description | Responses |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/admin/users` | Bearer (`role == "admin"`) | List all registered user accounts | `200 OK` (`List[UserPublicResponse]`), `403 Forbidden` |
| `PATCH` | `/api/v1/admin/users/{user_id}/status` | Bearer (`role == "admin"`) | Toggle user active status or role | `200 OK`, `403 Forbidden`, `404 Not Found` |

### 4.3 Recipes (`/api/v1/recipes`)

| Method | Path | Auth Required | Description | Responses |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/recipes` | Bearer Token | Create new recipe with ingredients & steps | `201 Created` (RecipeDetailResponse), `400 Bad Request`, `401 Unauthorized` |
| `GET` | `/api/v1/recipes/my-recipes` | Bearer Token | Fetch all recipes authored by current user | `200 OK` (`List[RecipeDetailResponse]`), `401 Unauthorized` |
| `GET` | `/api/v1/recipes/{recipe_id}` | None / Optional | Fetch detailed recipe by ID | `200 OK` (RecipeDetailResponse), `404 Not Found` |

---

## 5. Frontend Architecture & Routing

### 5.1 Route Mapping
- `/login`: Form for username/email + password, redirects to `/recipes/my-recipes` upon success.
- `/register`: Form for username, email, password, confirm password.
- `/profile`: View and edit user bio, culinary tags, and avatar preview.
- `/recipes/my-recipes`: Personal recipe dashboard displaying grid cards of recipes authored by the logged-in user.
- `/recipes/new`: Multi-section dynamic form for authoring recipes with dynamic "Add Ingredient" and "Add Step" rows.
- `/recipes/:id`: Detail view displaying ingredients list, cooking timing badges, and ordered step instructions.
- `/admin`: User management table (guarded by admin role check; redirects unauthorized users).

### 5.2 Client Services & State
- `src/services/api.ts`: Axios or Fetch wrapper intercepting outgoing requests to attach `Authorization: Bearer <token>`.
- `src/context/AuthContext.tsx`: Manages `currentUser`, `token`, `login()`, `logout()`, `isAuthenticated`, and `isAdmin`.

---

## 6. Edge Cases & Error Handling

1. **Duplicate Registration**: When email or username exists, backend returns `HTTP 409 Conflict` with `{"detail": "Username or email already registered"}`.
2. **Empty Ingredients or Steps**: Attempting to post a recipe with 0 ingredients or 0 steps returns `HTTP 422 Unprocessable Entity` via Pydantic validator.
3. **Invalid Token**: Expired or malformed JWT returns `HTTP 401 Unauthorized`. Frontend interceptor clears state and redirects to `/login`.
4. **Non-Admin Access to Admin Endpoints**: Standard user attempting to hit `/api/v1/admin/*` receives `HTTP 403 Forbidden`. Frontend shows access denied toast.
5. **Deleted/Missing Recipe**: Requesting `/api/v1/recipes/99999` returns `HTTP 404 Not Found` with `{"detail": "Recipe not found"}`.

---

## 7. Verification & Acceptance Test Suite

An implementation is considered complete only when the following automated tests pass:

### 7.1 Backend Test Matrix (`backend/tests/`)
- [ ] `test_register_user_success()`: Creates new user, returns 201, password is not returned in plain text.
- [ ] `test_register_duplicate_fails()`: Attempting duplicate email returns 409.
- [ ] `test_login_success_and_jwt()`: Valid login returns valid JWT token and user payload.
- [ ] `test_login_invalid_password()`: Wrong password returns 401.
- [ ] `test_create_recipe_authenticated()`: Authenticated user posts recipe with ingredients and steps; returns 201 with persisted IDs.
- [ ] `test_create_recipe_unauthenticated()`: Unauthenticated POST returns 401.
- [ ] `test_get_my_recipes()`: Only returns recipes matching `author_id == current_user.id`.
- [ ] `test_admin_endpoint_forbidden_for_user()`: Standard user token hitting `/api/v1/admin/users` returns 403.
- [ ] `test_admin_endpoint_allowed_for_admin()`: Admin token hitting `/api/v1/admin/users` returns 200.

### 7.2 Frontend Verification
- [ ] Submitting invalid registration highlights validation errors without hitting the backend.
- [ ] Successful login stores token and redirects to "My Recipes".
- [ ] Adding and removing ingredient/step rows dynamically updates the form state without DOM anomalies.
- [ ] "My Recipes" displays an empty-state illustration when the user has 0 recipes.
