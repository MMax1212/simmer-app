---
id: US4.1.3
story: US4.1
sprint: 4
assignee: Bryan Moreno
estimate_hours: 5
---

# Build Debounced Search Input Component with Live Dropdown & Keyboard Navigation in React

## Description
Serves **US4.1** (*Friend Search & Network*). Home cooks want to quickly find other users from anywhere in the app without having to type full usernames or trigger heavy page reloads.

This task implements the frontend search input component `UserSearchInput`:
- **Debounced Input:** 300ms debounce delay before triggering `api.searchUsers(q)` to avoid hammering the backend while typing.
- **Live Dropdown Overlay:** Displays up to 5-10 instant results displaying avatar/initials, username, bio snippet, follower count, and follow state.
- **Keyboard Navigation:** Full accessibility support with `ArrowDown`, `ArrowUp` to cycle through highlighted results, `Enter` to select/navigate, and `Escape` to close the dropdown.
- **Click-Outside Dismissal:** Automatically closes the dropdown menu when clicking anywhere outside the component.
- **Loading & Empty Feedback:** Displays clear spinner/skeleton state while fetching and friendly "No chefs found" feedback when no matches exist.
- **Inline Follow Action:** Allows users to immediately follow/unfollow discovered cooks directly from the search dropdown using `<FollowButton />`.

## Acceptance Criteria
1. Typing in the search input waits for a 300ms debounce period before dispatching `GET /api/v1/users/search?q={query}`.
2. If the query string has less than 1 non-whitespace character (or is cleared), the dropdown closes and no search request is dispatched.
3. Loading spinner indicator displays while network request is pending.
4. Dropdown renders matching users with avatar, username, follower count, and `<FollowButton />`.
5. Pressing `ArrowDown` highlights the next item in the dropdown list (wrapping or clamping).
6. Pressing `ArrowUp` highlights the previous item.
7. Pressing `Enter` when an item is highlighted navigates to the user's profile (`/profile/{username}`) or triggers the `onSelectUser` callback.
8. Pressing `Escape` or clicking outside the search container dismisses the dropdown.
9. Follow/unfollow toggle actions inside the dropdown update the user's state without closing the dropdown or losing focus.
10. Automated Vitest unit and interaction tests in `frontend/src/test/UserSearchInput.test.tsx` pass cleanly.
