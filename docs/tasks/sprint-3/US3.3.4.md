---
id: US3.3.4
story: US3.3
sprint: 3
assignee: Maximo Mora
estimate_hours: 3
---

# Implement Interactive Heart Like Button with Optimistic Counter and Toggle API Integration

## Description
Serves **US3.3** (*Likes & Comments on Community Posts*). Simmer users sharing dishes on the community feed want immediate visual feedback when interacting with posts. Waiting for network round-trips before updating the UI creates perceptible latency and detracts from the social cooking experience.

This task implements the reusable `LikeButton` React component featuring instant optimistic UI updates, animated heart transitions (using `lucide-react`), network-synchronized counts, and error-rollback mechanisms. It integrates with the `POST /api/v1/posts/{id}/like` endpoint contract defined in `docs/sprint3/spec.md`.

Slide-out comment drawer interactions (Task 3.3.5), bookmark toggle components (Task 3.4.3), and parent post card layout structuring (Task 3.1.4) are strictly out of scope.

## Specs
- **Component Interface (`LikeButtonProps` in `frontend/src/components/LikeButton.tsx`):**
  - `postId` (`number`, required): Unique ID of the community post being liked/unliked.
  - `initialLiked` (`boolean`, default: `false`): Current user's like status on initial load.
  - `initialLikesCount` (`number`, default: `0`): Total count of likes on the post.
  - `onToggle` (`(postId: number, liked: boolean, count: number) => void`, optional): Callback invoked after successful state change.
  - `disabled` (`boolean`, optional): Disables button interaction (e.g., when unauthenticated).

- **Visual & Interactive States:**
  - **Unliked State:** Gray/slate outline heart icon (`<Heart />`), subtle hover glow, accessible `aria-label="Like post"`, `aria-pressed="false"`.
  - **Liked State:** Filled rose/red heart icon (`fill-rose-500 text-rose-500`), subtle scale-pop animation (`scale-125` transition), accessible `aria-label="Unlike post"`, `aria-pressed="true"`.
  - **Counter Display:** Text counter displayed immediately adjacent to the heart icon reflecting current count.

- **API Endpoint Contract:**
  - Method & URL: `POST /api/v1/posts/{id}/like`
  - Headers: `Authorization: Bearer <token>`
  - Response (HTTP 200): `LikeToggleResponse`
    - `liked` (`boolean`): New like status on the server.
    - `likes_count` (`number`): Updated total like count.

- **Optimistic State & Edge Cases:**
  - **Optimistic Update:** When clicked, toggle active state immediately and increment ($+1$) or decrement ($-1$) the displayed count before the network request completes.
  - **In-Flight Lock / Debouncing:** Prevent multiple concurrent clicks while a request is in flight (`isSubmitting` guard).
  - **Error Rollback:** If the API returns a $4\text{xx}$ or $5\text{xx}$ error (or network failure), immediately roll back the state to the previous values and show a toast/alert notification.
  - **Boundary Guard:** Likes count cannot drop below `0`.

## Requirements
- Use React 18, TypeScript, Tailwind CSS, and `lucide-react` icons (existing project dependencies).
- No new external UI or animation libraries (use standard Tailwind transition utilities).
- Export API client helper `togglePostLike(postId: number)` in `frontend/src/services/api.ts` adhering to the spec contract.
- Place component at `frontend/src/components/LikeButton.tsx`.
- Cover with unit and interaction tests in `frontend/src/test/LikeButton.test.tsx` using Vitest and React Testing Library.
- No changes to existing backend schemas, models, or test suites.

## Acceptance criteria
1. The `LikeButton` renders with the correct initial visual state and count (outline heart when unliked; filled red heart when liked).
2. Clicking the button when unliked immediately flips the heart to filled red and increments the count by +1 without waiting for the server response.
3. Clicking the button when liked immediately flips the heart to outline gray and decrements the count by -1 without waiting for the server response.
4. An authenticated request is dispatched to `POST /api/v1/posts/{id}/like` via the API client on click.
5. When the server responds with HTTP 200, the button finalizes its state and count using the returned `likes_count`.
6. When the network request fails or returns an HTTP error, the button rolls back the heart color and count to their pre-click values.
7. Rapid successive clicks do not fire duplicate concurrent requests while a toggle request is in-flight.
8. Component has accessible keyboard support (`Enter` / `Space` activation) and correct `aria-label` / `aria-pressed` attributes.
9. All Vitest tests in `src/test/LikeButton.test.tsx` pass cleanly with 100% assertions satisfied.
