---
id: US3.4.3
story: US3.4
sprint: 3
assignee: Benjamin Ong
estimate_hours: 3
---

# Build Interactive BookmarkButton Component and Frontend API Client

## Description
Serves **US3.4** (*Bookmark / Save Posts*). This task implements the frontend API client helpers and a reusable, accessible `<BookmarkButton />` React component with instant optimistic UI updates and automatic rollback on network failure.

Backend endpoints (Task 3.4.2) and Profile tab integration (Task 3.4.4) are covered in separate tasks.

## Specs
- **API Client (`frontend/src/services/api.ts`):**
  - `togglePostBookmark(postId)`: Calls `POST /api/v1/posts/${postId}/bookmark`.
  - `getSavedPosts()`: Calls `GET /api/v1/users/me/saved-posts`.
- **`<BookmarkButton />` Component (`frontend/src/components/BookmarkButton.tsx`):**
  - Built with React 18, TypeScript, and `lucide-react`'s `<Bookmark />` icon.
  - Visual states: slate outline when unsaved with amber hover effect; filled amber (`fill-amber-500 text-amber-500`) when saved.
  - Optimistic UI: updates bookmark state immediately on click and rolls back to the previous state if the API request fails.
  - Accessibility: includes `aria-label` (`"Bookmark post"` / `"Remove bookmark"`), `aria-pressed`, and `aria-busy`.

## Requirements
- Match existing TypeScript and Tailwind CSS conventions in `frontend/src/components/`.
- Pass `npm test` and `npm run build` (`tsc && vite build`) with zero TypeScript errors.

## Acceptance criteria
1. `togglePostBookmark` and `getSavedPosts` are exported from `frontend/src/services/api.ts`.
2. `<BookmarkButton />` toggles visual state immediately on click and rolls back on API failure.
3. `<BookmarkButton />` exposes accessible `aria-label`, `aria-pressed`, and `aria-busy` attributes.
4. Frontend TypeScript compilation and Vite production build succeed with zero errors.
