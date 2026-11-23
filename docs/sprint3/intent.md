# Intent: Simmer Sprint 3 — Social Feed, Community Interactions & Following

**Author:** Team Simmer (Product Owner: Maximo Mora, Scrum Master: Ulises Diaz)  
**Status:** Approved  
**Date:** 2026-11-09  
**Target Milestone / Branch:** `sprint-3-social-feed` (CMPS 115 Sprint 3)  
**Reference Docs:** [Sprint_Plan_3.md](../Sprint_Plan_3.md), [Release_Plan_v1.1.md](../Release_Plan_v1.1.md), [Architecture_Design.md](../Architecture_Design.md)

---

## 1. Problem
Sprint 1 and Sprint 2 established a robust culinary foundation: users can authenticate, customize profile preferences, author structured recipes with ingredients/tools, search across recipes with faceted filters, and log their cooking history.

However, Simmer is not yet a social platform. Users cannot share dishes they cooked, post food photos, engage with fellow home chefs through likes or comments, bookmark inspiring community creations, or follow their favorite food creators. Furthermore, before implementing Sprint 4's multi-recipe grocery checklist generator, the team must evaluate ingredient normalization and unit arithmetic through an exploratory research spike.

---

## 2. Proposed Outcomes & Success Metrics
1. **Publish Food Posts (US3.1 — 5 pts):** Users can publish community dish posts featuring food photos, captions, and an optional interactive link to any recipe in the database.
2. **Post Lifecycle Management (US3.2 — 3 pts):** Authors can edit their post captions and photos or delete their posts, with strict author-only authorization guards (HTTP 403).
3. **Likes & Threaded Comments (US3.3 — 5 pts | Lead: Maximo Mora):** Users can engage with community posts via an animated heart like button (with optimistic UI updates) and discuss cooking tips in an expandable comment thread drawer.
4. **Bookmark / Saved Posts Collection (US3.4 — 3 pts):** Users can bookmark posts into a personal "Saved Posts" tab on their profile for quick future reference.
5. **Follow Network & Dual-Tab Feed (US3.5 — 3 pts):** Users can follow other creators to populate a dedicated "Following Feed", alongside a "Global Community Feed", with follower and following counts displayed on profiles.
6. **Grocery Checklist Algorithm Spike (SPK-3.1 — 2 pts):** Prototype and evaluation document for ingredient name stemming/normalization and fractional unit addition in preparation for Sprint 4 (**US4.2**).
7. **Quality & Test Integrity:** Automated Pytest and Vitest test suites cover all new social schemas, endpoints, and UI components while maintaining 100% pass rates across all 76 existing regression tests.

---

## 3. Non-Goals (Out of Scope for Sprint 3)
- **Do NOT build live WebSocket chat / direct messaging:** Private messaging is out of scope for the MVP release.
- **Do NOT wire external cloud object storage (S3/Cloudinary):** Continue using image URLs and verified image formats without requiring AWS credentials.
- **Do NOT implement Grocery Checklist UI:** The actual grocery list aggregation engine and UI belong to Sprint 4 (**US4.2**); Sprint 3 only conducts the algorithmic spike (**SPK-3.1**).
- **Do NOT build friend username discovery search:** Dedicated friend search and contact suggestions are scheduled for Sprint 4 (**US4.1**).

---

## 4. Guiding Principles & Trade-offs
- **Fan-Out-on-Read Feed Queries:** Based on findings in SPK-2.1, deliver timeline feeds using indexed SQL subqueries joining `posts` with `user_follows`. This avoids the complexity of Redis caches and timeline tables for our target scale.
- **Optimistic UI for Micro-Interactions:** When a user clicks "Like" or "Bookmark", the UI increments counts and highlights buttons immediately, rolling back only if the server responds with an error.
- **Relational Integrity with Cascades:** If an author deletes a post, database-level `ON DELETE CASCADE` must automatically remove all associated `post_likes`, `post_comments`, and `saved_posts` entries.
- **Strict Content Sanitization:** All user-submitted comment text and captions must be HTML-escaped and sanitized to eliminate Cross-Site Scripting (XSS) risks.

---

## 5. Affected Users & Systems
- **Users:** Home cooks sharing dishes, food lovers discovering recipes, and creators building a following.
- **Systems & Codebases:**
  - `backend/app/models/`: `post.py`, `post_like.py`, `post_comment.py`, `saved_post.py`, `user_follow.py`.
  - `backend/app/api/`: `posts.py` (CRUD, likes, comments, bookmarking), `users.py` (follow/unfollow, saved posts, timeline feed).
  - `backend/migrations/`: Alembic migrations for social tables, foreign keys, and unique composite indexes.
  - `frontend/src/pages/`: `Home.tsx` (dual-tab Global vs. Following feed), `Profile.tsx` (Saved Posts tab, follow counts).
  - `frontend/src/components/`: `PostCard.tsx`, `PostFormModal.tsx`, `CommentDrawer.tsx`, `HeartButton.tsx`, `BookmarkButton.tsx`, `FollowButton.tsx`.

---

## 6. Constraints & Guardrails
- **Idempotency:** Liking an already-liked post unlikes it; bookmarking a saved post unbookmarks it. Double-clicking must never create duplicate records.
- **Self-Follow Prohibition:** Users cannot follow themselves (`follower_id != following_id`).
- **Pagination Limits:** Feed queries and comment lists enforce `limit <= 50` and `offset >= 0` to safeguard server memory.
- **Mobile Responsive Design:** The slide-out comment drawer and post cards must fit cleanly on mobile viewports without horizontal scrolling.

---

## 7. High-Level Failure Behavior
- **Deleted Post Fallback:** If a post is deleted while bookmarked, the saved posts grid handles missing post references gracefully without crashing.
- **Unauthenticated Engagement:** Clicking like, comment, or bookmark while logged out prompts a clean toast notification: *"Please log in to like or comment on posts"*, redirecting to `/login`.
- **Empty Feed State:** When a new user views their "Following Feed" and follows nobody, display: *"You aren't following anyone yet! Explore the Global Community Feed to discover great home cooks."* with a button switching to the Global tab.

---

## 8. High-Level Acceptance Scenarios
- **Scenario 1 (Publish Dish Post with Recipe Link):**
  - *Given* an authenticated user on the home feed,
  - *When* they click "Share a Dish", enter a caption, paste a food photo URL, select their "Garlic Pasta" recipe, and submit,
  - *Then* the post appears at the top of the Global Feed showing their avatar, photo, caption, and an interactive recipe card preview.
- **Scenario 2 (Liking and Commenting — US3.3 Lead: Maximo Mora):**
  - *Given* a user viewing a community post with 4 likes,
  - *When* they click the heart icon and submit a comment *"Made this tonight, delicious!"*,
  - *Then* the heart turns red, like count increments to 5, and their comment appears at the top of the comment thread.
- **Scenario 3 (Following and Personalized Timeline):**
  - *Given* User A follows Chef Max,
  - *When* User A clicks the "Following" tab on the home feed,
  - *Then* User A sees posts authored by Chef Max in reverse-chronological order.
- **Scenario 4 (Bookmarking to Saved Posts):**
  - *Given* a user browsing the community feed,
  - *When* they click the bookmark ribbon icon on a post,
  - *Then* the ribbon fills in, and the post appears in the "Saved Posts" tab on their profile.

---

## 9. Open Questions & Technical Spikes
- **SPK-3.1 (Algorithm Spike):** Research and benchmark natural language ingredient name stemming (e.g., `"chopped garlic cloves"` $\rightarrow$ `"garlic"`) and fractional unit arithmetic (e.g., $1/4\text{ cup} + 2\text{ tbsp}$) for Sprint 4's grocery list generator.
