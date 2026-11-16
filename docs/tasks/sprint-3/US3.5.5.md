---
id: US3.5.5
story: US3.5
sprint: 3
assignee: Bryan Moreno
estimate_hours: 4
---

# Build Tabbed Home Feed UI (Following Feed vs. Global Community Feed)

## Description
Serves **US3.5** (*Follow Users & Following Feed*). Simmer home cooks need a dedicated, interactive timeline feed where posts published by creators they follow are front-and-center, with seamless toggling between their personalized "Following Feed" and the "Global Community Feed".

This task builds the tabbed feed UI on the Home page (`frontend/src/pages/Home.tsx`) and the feed card component (`frontend/src/components/FeedCard.tsx`), integrating the fan-out-on-read timeline API (`GET /api/v1/feed`), interactive `<FollowButton />` controls, and `<LikeButton />` actions.

## Specs & Features
- **Tab Navigation:**
  - Accessible tab switcher (`role="tablist"` / `role="tab"`) between "Following Feed" (`mode="following"`) and "Global Community Feed" (`mode="global"`).
  - Default tab selection: Authenticated users land on "Following Feed"; anonymous visitors land on "Global Community Feed".
- **Unauthenticated Handling:**
  - When anonymous visitors click "Following Feed", displays a sign-in callout prompting them to log in to personalize their feed.
- **Empty State UX:**
  - If a user follows nobody or their network has not posted, displays a friendly empty state ("Your following feed is empty! Follow fellow home cooks to see their creations here.") with a one-click CTA to explore the Global Community Feed.
- **Feed Card Display (`<FeedCard />`):**
  - Author header: Profile avatar (with fallback letter badge), username, post timestamp, and embedded `<FollowButton />`.
  - Media display: High-resolution culinary post image with full aspect ratio preservation.
  - Caption: Post description formatted with whitespace preservation.
  - Linked recipe chip: Clickable card preview showing recipe title, cooking duration, and difficulty rating.
  - Action footer: Interactive `<LikeButton />` component.

## Acceptance Criteria
1. Displays tabs for "Following Feed" and "Global Community Feed" with accessible `role="tab"` and `aria-selected` attributes.
2. Authenticated users default to "Following Feed" and load posts filtered by their followed network.
3. Empty Following Feed renders a helpful empty state with a call-to-action to switch to the Global Community Feed.
4. Clicking "Global Community Feed" fetches and displays posts across the global community.
5. Anonymous visitors selecting "Following Feed" are prompted with a sign-in callout directing them to `/login`.
6. Feed cards render author details with interactive `<FollowButton />` and `<LikeButton />`.
7. 100% of automated tests pass in `frontend/src/test/feed.test.tsx`.
