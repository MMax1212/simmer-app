# Intent: Simmer Sprint 1 — Core Auth, Profiles & Personal Recipe Library

**Author:** Team Simmer (Product Owner: Maximo Mora)  
**Status:** Approved  
**Date:** 2026-10-12  
**Target Milestone / Branch:** `sprint-1-foundation` (CMPS 115 Sprint 1)  
**Reference Docs:** [Sprint_Plan_1.md](./Sprint_Plan_1.md), [Architecture_Design.md](./Architecture_Design.md)

---

## 1. Problem
Currently, Simmer is a greenfield project with no running architecture. Users have no way to create accounts, authenticate securely, customize their culinary profile, or record and view their personal recipes. We need an end-to-end operational vertical slice establishing the frontend (React/Vite/TS), backend (FastAPI/Python), and persistence layer (SQLite/SQLAlchemy).

## 2. Proposed Outcomes & Success Metrics
1. **Secure Authentication & RBAC (US1.1 & US1.2):** Users can register, log in with password hashing, and obtain JWT tokens. Admin users possess role flags permitting administrative oversight.
2. **User Profile Configuration (US1.3):** Authenticated users can view and update their bio, culinary tags, and avatar image URL.
3. **Recipe Authoring & Personal Library (US1.4 & US1.5):** Users can create structured recipes (title, ingredients, prep/cook time, instructions) and immediately view their personal collection in a dedicated "My Recipes" tab.
4. **CI & Testing Foundation:** Basic test suite (Pytest on backend, Vitest/Jest on frontend) passing locally and in CI.

## 3. Non-Goals (Out of Scope for Sprint 1)
- **Do NOT implement social interactions:** No public feed, following/followers, recipe likes, comments, or public sharing (reserved for Sprint 2).
- **Do NOT implement external cloud uploads:** Do not integrate live AWS S3 or Cloudinary APIs yet; use valid image URLs or mock placeholders for recipe/avatar images.
- **Do NOT build advanced search or discovery:** No semantic search, ingredient auto-complete, or recommendation algorithms (Sprint 2/3).
- **Do NOT build meal planning or grocery lists:** Reserved for Sprint 3.

## 4. Guiding Principles & Trade-offs
- **Simplicity Over Abstraction:** Keep router and service logic straightforward; do not build unnecessary microservice wrappers or complex message queues.
- **Decoupled Architecture:** Strict separation between the React frontend and FastAPI backend communicating strictly over REST/JSON.
- **SQLite for Local Dev:** Maintain local SQLite compatibility using SQLAlchemy migrations before targeting staging PostgreSQL.
- **Self-Testing Agents:** Every backend route must have an accompanying automated test in `tests/` asserting status codes and response models.

## 5. Affected Users & Systems
- **Users:** End Users (Home Cooks) and System Administrators.
- **Systems & Codebases:**
  - `backend/`: FastAPI application (`/auth`, `/users`, `/recipes`), SQLAlchemy models, Alembic migrations, Pytest suite.
  - `frontend/`: React + TypeScript SPA (Auth forms, Profile page, Recipe editor, "My Recipes" dashboard).
  - `database`: Relational tables (`users`, `roles`, `recipes`, `ingredients`, `instructions`).

## 6. Constraints & Guardrails
- **Security:** Passwords must be hashed using `bcrypt` or `argon2`. Plaintext passwords must never appear in logs or API responses.
- **Authentication:** Standard JWT (Bearer token) passed in HTTP headers with expiration handling.
- **RBAC:** Admin endpoints must be protected by middleware verifying `role == "admin"`.
- **Frontend Stack:** React, TypeScript, and Tailwind CSS/Vite (as specified in architecture docs). No arbitrary third-party UI libraries without prior approval.

## 7. High-Level Failure Behavior
- **Invalid Auth Credentials:** Return clear 401 Unauthorized messages with user-friendly error banners (no generic 500 errors or uncaught promise rejections).
- **Unauthorized / Role Escalation:** Non-admin users attempting to reach `/admin` must receive 403 Forbidden and be redirected gracefully to home/dashboard.
- **Form Validation Failures:** Client-side dynamic validation on recipe/profile fields (e.g., missing recipe title, invalid email format) before submission.

## 8. High-Level Acceptance Scenarios
- **Scenario 1 (New User Onboarding to Recipe Creation):**
  - *Given* an unregistered visitor,
  - *When* they register an account, log in, navigate to "New Recipe", fill in ingredients/steps, and click "Save",
  - *Then* the recipe is saved to the database and appears immediately under their "My Recipes" tab.
- **Scenario 2 (RBAC Protection):**
  - *Given* a logged-in standard user,
  - *When* they attempt to make an API call to the admin user management endpoint,
  - *Then* the request returns HTTP 403 and no administrative data is exposed.

## 9. Open Questions & Technical Spikes
- Should JWT tokens be stored in `localStorage` or `HttpOnly` cookies for local dev simplicity? *(For Sprint 1: Bearer token via Authorization header / localStorage).*
- What default culinary tags should pre-populate the profile selector? *(Italian, Mexican, Vegan, Quick & Easy, Baking).*
