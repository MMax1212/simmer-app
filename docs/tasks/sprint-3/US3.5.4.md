---
id: US3.5.4
story: US3.5
sprint: 3
assignee: Bryan Moreno
estimate_hours: 3
---

# Build Interactive FollowButton Component in React

## Description
Serves **US3.5** (*Follow Users & Following Feed*). Simmer home cooks want an intuitive, responsive way to follow and unfollow creators directly from user profiles, author headers, and recipe cards.

This task creates the reusable `<FollowButton />` component in React with:
- Optimistic UI updates (+1 / -1 follower count immediately on click).
- Seamless rollback and user-facing error reporting if the API request fails.
- Distinct visual states: "Follow" (prominent rose action button) vs. "Following" (subtle slate pill), with dynamic "Unfollow" indicator on hover.
- Automatic self-follow suppression (`currentUserId === targetUserId`).
- In-flight request debouncing to prevent concurrent duplicate requests.

## Component Props (`FollowButtonProps`)
- `targetUserId` (`number`, required): The database user ID of the creator to follow/unfollow.
- `targetUsername` (`string`, optional): Used to build accessible aria-labels (e.g., `Follow @jane_cooks`).
- `initialFollowing` (`boolean`, default: `false`): Initial follow status for the logged-in viewer.
- `initialFollowersCount` (`number`, default: `0`): Initial follower count.
- `showCount` (`boolean`, default: `false`): Displays the numerical follower count badge.
- `currentUserId` (`number`, optional): Currently logged-in user ID; if equal to `targetUserId`, component renders `null` to prevent self-following.
- `size` (`"sm" | "md"`, default: `"sm"`): Compact styling for feed headers vs. standard for profile headers.
- `disabled` (`boolean`, default: `false`): Disables button interaction.
- `className` (`string`, optional): Additional container styling classes.
- `onToggle` (`function`, optional): Callback fired with `(targetUserId: number, following: boolean, followersCount?: number)`.

## Acceptance Criteria
1. Renders "Follow" button with `aria-pressed="false"` when `initialFollowing={false}`.
2. Renders "Following" button with `aria-pressed="true"` when `initialFollowing={true}`.
3. Displays numerical follower count badge when `showCount={true}`.
4. Suppresses rendering (`null`) when `currentUserId === targetUserId` to prevent self-following.
5. Optimistically toggles button label and increments/decrements follower count immediately upon click before API resolution.
6. Hovering over a followed button dynamically switches label to "Unfollow" with rose styling.
7. Dispatches authenticated `POST /api/v1/users/{userId}/follow` to backend.
8. Automatically rolls back state to original values and renders an accessible error alert (`role="alert"`) if network request fails.
9. Executes `onToggle` callback with updated following state and count.
10. Disallows concurrent duplicate API requests while an action is in flight.
11. 100% of automated tests pass in `frontend/src/test/FollowButton.test.tsx`.
