---
id: US3.3.5
story: US3.3
sprint: 3
assignee: Maximo Mora
estimate_hours: 5
---

# Implement Slide-Out Comment Thread Drawer with Real-Time Comment Authoring

## Description
Serves **US3.3** (*Likes & Comments on Community Posts*). Users exploring community dishes want to engage with recipes by asking cooking questions, sharing recipe modifications, and discussing culinary tips. 

This task implements the reusable `CommentDrawer` React component and associated API client methods. It features a slide-out drawer displaying discussion comments, a sticky bottom input field with real-time character counting, optimistic comment submission, and error-rollback handling.

Parent post card layout structuring (Task 3.1.4), heart like button (Task 3.3.4), and bookmark toggle components (Task 3.4.3) are strictly out of scope.

## Specs
- **Component Interface (`CommentDrawerProps` in `frontend/src/components/CommentDrawer.tsx`):**
  - `postId` (`number`, required): Unique ID of the community post.
  - `isOpen` (`boolean`, required): Controls drawer visibility.
  - `onClose` (`() => void`, required): Callback invoked when closing drawer (via close button, backdrop click, or `Escape` key).
  - `initialCommentCount` (`number`, optional): Displayed comment count for header.
  - `onCommentAdded` (`(comment: Comment) => void`, optional): Callback invoked after a comment is successfully posted.

- **Data Models (`frontend/src/types/post.ts` or `frontend/src/services/api.ts`):**
  - `Comment`:
    - `id`: `number`
    - `post_id`: `number`
    - `user_id`: `number`
    - `username`: `string`
    - `avatar_url`?: `string | null`
    - `content`: `string`
    - `created_at`: `string`
  - `CommentCreate`: `{ content: string }`

- **Visual & Interactive States:**
  - **Slide-Out Panel:** Positioned fixed on the right (or bottom on mobile) with accessible backdrop, `role="dialog"`, `aria-label="Comments drawer"`, and visible close button (`aria-label="Close comments"`).
  - **Scrollable Comment List:** Displays comments chronologically with author avatar (or fallback initials), username, relative timestamp, and sanitized comment text.
  - **Empty State:** When no comments exist, renders: *"No comments yet. Be the first to share your thoughts!"*.
  - **Loading State:** Shows an accessible loading indicator while fetching comments.
  - **Sticky Bottom Input Bar:** Text input / textarea with live character counter (`0/1000`) and a "Post" button.
  - **Validation & Disabled State:** "Post" button is disabled if comment is empty, whitespace-only, exceeds 1,000 characters, or while a submission is in-flight.

- **API Endpoint Contracts:**
  - `GET /api/v1/posts/{id}/comments` -> `Comment[]`
  - `POST /api/v1/posts/{id}/comments` -> `Comment` (Auth required, JSON body: `{ content: string }`, HTTP 201)

- **Optimistic State & Edge Cases:**
  - **Optimistic Append:** When user submits a comment, immediately append a temporary comment item to the list and clear the input field.
  - **In-Flight Lock:** Prevent duplicate submissions while a request is in flight (`isSubmitting` flag).
  - **Error Rollback:** If the API returns an error, remove the temporary comment, restore the user's drafted text, and display an error alert.
  - **Keyboard Support:** Pressing `Escape` closes the drawer.

## Requirements
- Use React 18, TypeScript, Tailwind CSS, and `lucide-react` icons (existing project dependencies).
- No new external UI libraries.
- Export API client helpers `getPostComments(postId: number)` and `createPostComment(postId: number, content: string)` in `frontend/src/services/api.ts`.
- Place component at `frontend/src/components/CommentDrawer.tsx`.
- Cover with unit and interaction tests in `frontend/src/test/CommentDrawer.test.tsx` using Vitest and React Testing Library.
- No changes to existing backend schemas, models, or test suites.

## Acceptance criteria
1. The `CommentDrawer` renders with accessible dialog attributes (`role="dialog"`) when `isOpen=true`, and does not render content when `isOpen=false`.
2. Clicking the close button, clicking the backdrop, or pressing the `Escape` key triggers the `onClose` callback.
3. When opened, it fetches and displays comments from `GET /api/v1/posts/{id}/comments`.
4. Displays an empty state message when a post has no comments.
5. The submit button is disabled when the input is empty or whitespace-only, and input length cannot exceed 1,000 characters.
6. Submitting a valid comment dispatches an authenticated `POST /api/v1/posts/{id}/comments` request.
7. Submitting a comment optimistically adds it to the list immediately before the network response completes.
8. If the network request fails, the optimistic comment is rolled back, the user's drafted text is restored, and an error alert is displayed.
9. All Vitest tests in `frontend/src/test/CommentDrawer.test.tsx` pass cleanly with all test names prefixed with `US3.3.5`.
