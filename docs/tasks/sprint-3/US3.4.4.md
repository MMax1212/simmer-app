---
id: US3.4.4
story: US3.4
sprint: 3
assignee: Benjamin Ong
pr: https://github.com/MMax1212/simmer-app/pull/44
estimate_hours: 3
---

# Add "Saved Posts" Tab to Profile Page

## Description
Serves **US3.4** (*Bookmark / Save Posts*). This task integrates the saved posts collection into the user's Profile page (`frontend/src/pages/Profile.tsx`) so users can view and manage their bookmarked posts in one place.

Backend endpoints (Task 3.4.2) and the standalone `<BookmarkButton />` component (Task 3.4.3) are covered in separate tasks.

## Specs
- **Profile Navigation (`frontend/src/pages/Profile.tsx`):**
  - Expands profile tabs to three views: `"profile"`, `"history"`, and `"saved"`.
  - Lazy-loads saved posts via `getSavedPosts()` when the `"saved"` tab is activated.
- **Saved Posts View:**
  - Displays saved post cards with recipe title, author info, image, creation date, and integrated `<BookmarkButton />`.
  - Includes loading state and empty state (`"No saved posts yet"`).

## Requirements
- Reuse `<BookmarkButton />` and `getSavedPosts()` from `frontend/src/services/api.ts`.
- Keep existing `"profile"` and `"history"` tab behavior intact.
- Pass `npm test` and `npm run build` with zero errors.

## Acceptance criteria
1. The Profile page renders `"profile"`, `"history"`, and `"saved"` tabs.
2. Selecting the `"saved"` tab fetches and displays the user's bookmarked posts.
3. Dedicated loading and empty states (`"No saved posts yet"`) render appropriately.
4. Users can unbookmark posts directly from the Saved Posts view via `<BookmarkButton />`.
