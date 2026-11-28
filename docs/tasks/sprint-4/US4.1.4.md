---
id: US4.1.4
story: US4.1
sprint: 4
assignee: Bryan Moreno
estimate_hours: 4
---

# Build Dedicated "Find Chefs & Friends" Directory Page with Profile Summary Cards and Follow Toggles

## Description
Serves **US4.1** (*Friend Search & Network*). Home cooks need a dedicated, full-screen community directory page (`/friends`) to discover new chefs, search for friends by username, view chef profiles (bio, culinary preferences, social network stats), and instantly follow/unfollow users.

This task implements the directory page `FindFriends.tsx`:
- **Route & Navigation:** Registered at `/friends` in `App.tsx` and linked from `Navbar.tsx` as "Find Friends".
- **URL Query Sync:** Synchronizes with URL query parameter `?q=...` so selecting a cook or following search links lands directly on the filtered results.
- **Chef Profile Summary Cards:** Responsive grid rendering:
  - User avatar (or custom colored initials badge)
  - Username (`@username`)
  - Bio snippet and culinary preference badges/pills
  - Social network stats: `followers_count` and `following_count`
  - Instant interactive `<FollowButton />` with optimistic updates
- **Cold-Start Discovery:** When no search query is present, loads the default directory of active home cooks on the platform.
- **Search Header & Filter Controls:** Clean search bar with instant debouncing and clear button.
- **Empty States & Loading Feedback:** Dedicated feedback when searching for cooks that don't exist with a quick "Clear search" action.

## Acceptance Criteria
1. Navigating to `/friends` loads and displays the chef directory grid.
2. If URL contains `?q=searchterm`, the search input is initialized with `searchterm` and filtered results are retrieved from `api.searchUsers("searchterm")`.
3. Chef cards display avatar, username, bio (if present), culinary preferences (if present), and follower/following counts.
4. Each card contains an interactive `<FollowButton />` that allows immediate follow/unfollow.
5. Following/unfollowing a user on a card updates that card's follower count and relationship state in place.
6. When no users match the query, an empty state is displayed with a "Clear search" button to reset the directory.
7. Automated Vitest tests in `frontend/src/test/FindFriends.test.tsx` verify initial directory loading, query parameter synchronization, empty states, and follow button interactions.
