# Simmer External & Public REST API Specification

**Service Name:** Simmer Backend API  
**Base URL:** `http://localhost:8000` (Local Development)  
**API Version Prefix:** `/api/v1`  
**Interactive Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)  
**Interactive ReDoc UI:** [http://localhost:8000/redoc](http://localhost:8000/redoc)  

---

## 1. Overview & Architectural Conventions

All external endpoints follow standard **RESTful HTTP design principles**:
- **Format:** All requests and responses use `application/json` with UTF-8 encoding.
- **Authentication:** Protected endpoints require a valid JSON Web Token (JWT) supplied in the standard HTTP header:
  ```http
  Authorization: Bearer <jwt_access_token>
  ```
- **Error Handling:** Errors return standard HTTP status codes ($4\text{xx}$ client errors, $5\text{xx}$ server errors) with a JSON error payload:
  ```json
  {
    "detail": "Error description or validation message"
  }
  ```
  Validation failures return HTTP `422 Unprocessable Entity` containing field-level error locations:
  ```json
  {
    "detail": [
      {
        "loc": ["body", "caption"],
        "msg": "field required",
        "type": "value_error.missing"
      }
    ]
  }
  ```

---

## 2. API Endpoint Directory

| Method | Endpoint | Auth Required | Description |
| :--- | :--- | :---: | :--- |
| **Authentication** | | | |
| `POST` | `/api/v1/auth/register` | None (Public) | Register a new user account with email, username, and password |
| `POST` | `/api/v1/auth/login` | None (Public) | Authenticate credentials; returns JWT access token and user profile |
| `POST` | `/api/v1/auth/token` | None (Public) | OAuth2-compatible form login (powers Swagger UI authorization) |
| `GET` | `/api/v1/auth/me` | Bearer Token | Retrieve currently authenticated user identity and role |
| **Users & Profiles** | | | |
| `PUT` | `/api/v1/users/me` | Bearer Token | Update personal profile (bio, avatar URL, culinary preferences) |
| `GET` | `/api/v1/users/me/cooking-history` | Bearer Token | Retrieve authenticated user's personal cooking log history |
| `GET` | `/api/v1/users/{username}` | None (Public) | Look up public chef profile by username |
| **Recipes & Search** | | | |
| `GET` | `/api/v1/recipes` | None (Public) | Search recipes by keyword (`q`), dietary tags (`tag`), cuisine, and difficulty |
| `POST` | `/api/v1/recipes` | Bearer Token | Author a new structured recipe with ingredients, tools, and steps |
| `GET` | `/api/v1/recipes/my-recipes` | Bearer Token | List all recipes authored by the authenticated user with pagination |
| `GET` | `/api/v1/recipes/{recipe_id}` | None (Public) | Read complete recipe details by ID |
| `PUT` | `/api/v1/recipes/{recipe_id}` | Bearer Token (Author Only) | Update an existing recipe authored by the user |
| `DELETE` | `/api/v1/recipes/{recipe_id}` | Bearer Token (Author/Admin) | Delete a recipe and cascade child ingredients/steps |
| `POST` | `/api/v1/recipes/{recipe_id}/complete` | Bearer Token | Mark a recipe as cooked with optional rating (1–5) and notes (60s cooldown) |
| **Social Feed & Interactions** | | | |
| `POST` | `/api/v1/posts/{post_id}/like` | Bearer Token | Toggle like status on a community dish post |
| `GET` | `/api/v1/posts/{post_id}/comments` | None (Public) | Retrieve list of discussion comments for a post |
| `POST` | `/api/v1/posts/{post_id}/comments` | Bearer Token | Post a discussion comment under a post (1–1,000 characters) |
| **Administration (RBAC)** | | | |
| `GET` | `/api/v1/admin/users` | Bearer Token (Admin) | List all registered accounts with optional role/active filters |
| `PATCH` | `/api/v1/admin/users/{user_id}/status` | Bearer Token (Admin) | Deactivate/reactivate user accounts or update system roles |
| `GET` | `/api/v1/admin/audit-logs` | Bearer Token (Admin) | Inspect historical administrative audit trail with pagination |
| `GET` | `/api/v1/admin/stats` | Bearer Token (Admin) | Retrieve aggregated platform metrics (users, recipes, active counts) |
| **System** | | | |
| `GET` | `/api/health` | None (Public) | Check backend server availability and health status |

---

## 3. Detailed Endpoint Contracts

### 3.1 Authentication Endpoints

#### Register Account
`POST /api/v1/auth/register`
* **Access:** Public
* **Request Body:**
  ```json
  {
    "email": "chef@example.com",
    "username": "chef_mario",
    "password": "SecurePassword123!"
  }
  ```
* **Success Response (201 Created):**
  ```json
  {
    "id": 1,
    "email": "chef@example.com",
    "username": "chef_mario",
    "role": "user",
    "is_active": true,
    "bio": null,
    "avatar_url": null,
    "culinary_preferences": []
  }
  ```
* **Errors:** `400 Bad Request` (Email or username already registered), `422 Unprocessable Entity` (Password under 8 characters).

---

#### User Login
`POST /api/v1/auth/login`
* **Access:** Public
* **Request Body:**
  ```json
  {
    "username_or_email": "chef_mario",
    "password": "SecurePassword123!"
  }
  ```
* **Success Response (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "email": "chef@example.com",
      "username": "chef_mario",
      "role": "user",
      "is_active": true,
      "bio": null,
      "avatar_url": null,
      "culinary_preferences": []
    }
  }
  ```
* **Errors:** `401 Unauthorized` (Invalid credentials or deactivated account).

---

### 3.2 Recipe Endpoints

#### Search & Filter Recipes
`GET /api/v1/recipes`
* **Access:** Public
* **Query Parameters:**
  - `q` (string, optional): Search keyword matched across titles, descriptions, and ingredients.
  - `tag` (string, optional): Filter by tag (e.g. `quick` or `#healthy`).
  - `cuisine` (string, optional): Filter by cuisine (e.g. `Italian`, `Mexican`, `Asian`).
  - `meal_type` (string, optional): Filter by meal type (e.g. `dinner`, `breakfast`).
  - `difficulty` (string, optional): Filter by difficulty (`easy`, `medium`, `hard`).
  - `limit` (integer, default: 20, min: 1, max: 100): Maximum records per page.
  - `offset` (integer, default: 0): Records to skip for pagination.
* **Success Response (200 OK):**
  ```json
  {
    "total": 1,
    "limit": 20,
    "offset": 0,
    "items": [
      {
        "id": 10,
        "title": "Classic Margherita Pizza",
        "description": "Crispy crust with San Marzano tomatoes, fresh mozzarella, and basil.",
        "cuisine": "Italian",
        "meal_type": "dinner",
        "difficulty": "medium",
        "prep_time_mins": 20,
        "cook_time_mins": 15,
        "servings": 2,
        "image_url": "https://images.unsplash.com/pizza.jpg",
        "author_id": 1,
        "owner": {
          "id": 1,
          "username": "chef_mario"
        },
        "tags": ["#italian", "#pizza", "#dinner"]
      }
    ]
  }
  ```

---

#### Create Recipe
`POST /api/v1/recipes`
* **Access:** Authenticated (`Bearer <token>`)
* **Request Body:**
  ```json
  {
    "title": "Creamy Tuscan Garlic Pasta",
    "description": "Savory fettuccine with spinach and sun-dried tomatoes.",
    "cuisine": "Italian",
    "meal_type": "dinner",
    "difficulty": "easy",
    "prep_time_mins": 10,
    "cook_time_mins": 20,
    "servings": 4,
    "image_url": "https://images.unsplash.com/pasta.jpg",
    "ingredients": [
      { "name": "fettuccine", "amount": 8.0, "unit": "oz" },
      { "name": "garlic cloves", "amount": 4.0, "unit": "count" }
    ],
    "steps": [
      { "step_number": 1, "instruction": "Boil pasta in salted water until al dente." },
      { "step_number": 2, "instruction": "Saute minced garlic in olive oil." }
    ],
    "tools": ["Large Pot", "Garlic Press"],
    "tags": ["#italian", "#quick", "#dinner"]
  }
  ```
* **Success Response (201 Created):** Full `RecipeOut` object containing persisted IDs.
* **Errors:** `401 Unauthorized` (Missing or invalid token), `422 Unprocessable Entity` (Missing required fields).

---

#### Mark Recipe as Cooked (Cooking History)
`POST /api/v1/recipes/{recipe_id}/complete`
* **Access:** Authenticated (`Bearer <token>`)
* **Request Body:**
  ```json
  {
    "notes": "Added extra roasted garlic. Turned out fantastic!",
    "rating": 5
  }
  ```
* **Success Response (200 OK):**
  ```json
  {
    "id": 4,
    "recipe_id": 10,
    "cooked_at": "2026-11-19T21:40:00Z",
    "notes": "Added extra roasted garlic. Turned out fantastic!",
    "rating": 5
  }
  ```
* **Errors:** `400 Bad Request` ("Recipe was already marked as cooked within the last 60 seconds"), `422 Unprocessable Entity` (Rating not between 1 and 5).

---

### 3.3 Community Social Interactions (US3.3)

#### Toggle Post Like
`POST /api/v1/posts/{post_id}/like`
* **Access:** Authenticated (`Bearer <token>`)
* **Success Response (200 OK):**
  ```json
  {
    "liked": true,
    "likes_count": 14
  }
  ```
* **Errors:** `401 Unauthorized` (Not logged in), `404 Not Found` (Post does not exist).

---

#### Create Discussion Comment
`POST /api/v1/posts/{post_id}/comments`
* **Access:** Authenticated (`Bearer <token>`)
* **Request Body:**
  ```json
  {
    "content": "Can I substitute heavy cream with coconut milk for this sauce?"
  }
  ```
* **Success Response (201 Created):**
  ```json
  {
    "id": 82,
    "post_id": 5,
    "user_id": 1,
    "username": "chef_mario",
    "avatar_url": null,
    "content": "Can I substitute heavy cream with coconut milk for this sauce?",
    "created_at": "2026-11-19T21:45:00Z"
  }
  ```
* **Errors:** `401 Unauthorized`, `422 Unprocessable Entity` (Content length not between 1 and 1,000 characters).

---

### 3.4 Administrative Operations (US1.2)

#### List System Users
`GET /api/v1/admin/users`
* **Access:** Admin Only (`role == "admin"`)
* **Query Parameters:**
  - `role` (string, optional): Filter by `"user"` or `"admin"`.
  - `is_active` (boolean, optional): Filter active/deactivated accounts.
* **Success Response (200 OK):** List of `UserPrivate` objects.
* **Errors:** `403 Forbidden` ("Admins only").

---

#### Toggle User Account Status
`PATCH /api/v1/admin/users/{user_id}/status`
* **Access:** Admin Only (`role == "admin"`)
* **Request Body:**
  ```json
  {
    "is_active": false,
    "role": "user"
  }
  ```
* **Success Response (200 OK):** Updated user object. Creates an immutable audit record in `admin_audit`.
* **Errors:** `400 Bad Request` ("Admins can't change their own account here"), `403 Forbidden` ("Admins only"), `404 Not Found`.

---

### 3.5 System Health

#### Health Check
`GET /api/health`
* **Access:** Public
* **Success Response (200 OK):**
  ```json
  {
    "status": "ok",
    "app": "Simmer Backend",
    "version": "1.0.0"
  }
  ```
