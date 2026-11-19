# Code Standards
**Team:** Team Simmer | **Stack:** Python, FastAPI, TypeScript, React | **Version:** 1.0

## Style Guide Reference
We follow the **PEP 8 & Google Python Style Guide** for backend Python, and the **Google TypeScript Style Guide** with **Airbnb React Guidelines** for frontend TypeScript. Code quality and type safety are verified via `npm run build` (`tsc`) and `pytest`.

## Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Variables (TypeScript) | camelCase | `recipeCount`, `selectedCuisine` |
| Variables (Python) | snake_case | `recipe_id`, `cook_time_mins` |
| Boolean variables | `is`/`has`/`can` prefix | `isLoading`, `hasLiked`, `is_active` |
| Functions (TypeScript) | verb + noun, camelCase | `searchRecipes()`, `togglePostLike()` |
| Functions (Python) | verb + noun, snake_case | `get_current_user()`, `search_recipes()` |
| React components | PascalCase | `RecipeCard`, `LikeButton`, `CommentDrawer` |
| Database Models (ORM) | PascalCase, singular | `User`, `Recipe`, `CompletedRecipe` |
| Database Tables | snake_case, plural | `users`, `recipes`, `completed_recipes` |
| Constants | UPPER_SNAKE_CASE | `MAX_COMMENT_LENGTH = 1000`, `STANDARD_UNITS` |
| Types / Interfaces / DTOs | PascalCase, no `I` prefix | `Recipe`, `UserPrivate`, `LikeButtonProps` |

**No magic numbers:** Replace hardcoded numbers with descriptive constants (e.g., replace `if (rating > 5)` with `if (rating > MAX_RATING)`, or replace `401` with `status.HTTP_401_UNAUTHORIZED`).

## Formatting
- **Indentation:** 
  - Frontend (TSX/TS/CSS): 2 spaces (no tabs)
  - Backend (Python): 4 spaces (no tabs, PEP 8)
- **Line length:** max 100 characters
- **Quotes:** double quotes for Python (`"title"`); double quotes or single quotes consistent within files for TypeScript
- **Semicolons:** always required in TypeScript
- **Braces:** opening brace on same line as declaration (`function LikeButton() { ... }`)

Enforced automatically before push — run `npm run build` (`tsc`) and `pytest` locally.

## Best Practices
- **DRY (Don't Repeat Yourself):** Centralize shared HTTP calls in `frontend/src/services/api.ts` and shared backend authentication/database injection in `backend/app/api/deps.py`.
- **Single Responsibility:** Each function or component does one thing. If a React component handles data fetching, business logic, and complex rendering, split it into sub-components or custom hooks.
- **Clarity over cleverness:** Write code for the next reader. Use explicit Pydantic DTOs and typed TypeScript props rather than unreadable one-liners.
- **Fail Fast & Defense-in-Depth:** Validate all inputs at the API boundary using Pydantic schemas; rely on React's native JSX escaping (`{comment.content}`) to prevent XSS.
- **No commented-out code:** Delete unused code and debug `console.log` statements. Git history preserves all previous iterations.
