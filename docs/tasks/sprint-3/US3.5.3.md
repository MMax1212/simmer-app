---
id: US3.5.3
story: US3.5
sprint: 3
assignee: Bryan Moreno
estimate_hours: 4
---

# Implement Timeline Feed Query Endpoint (Fan-Out-On-Read Delivery)

## Description
Serves **US3.5** (*Follow Users & Following Feed*). Simmer home cooks want to see the latest food creations published by the creators they follow. Building directly on Bryan Moreno's architectural findings from **SPK-2.1** (*Social Feed Architecture Spike*), this task implements the timeline feed endpoint (`GET /api/v1/feed`) utilizing a fan-out-on-read relational subquery.

This endpoint supports two feed modes:
1. `mode="following"`: Chronological feed filtered by the caller's follower network (`author_id IN (SELECT following_id FROM user_follows WHERE follower_id = current_user.id)`). Requires authentication.
2. `mode="global"`: Global community discovery feed delivering all food posts chronologically. Accessible publicly.

## Specs
- **Endpoint:** `GET /api/v1/feed`
- **Query Parameters:**
  - `mode` (`str`, default: `"following"`): Mode selector (`"following"` or `"global"`).
  - `limit` (`int`, default: `20`, min: `1`, max: `100`): Pagination size limit.
  - `offset` (`int`, default: `0`, min: `0`): Pagination offset.
- **Headers:** `Authorization: Bearer <token>` (Required when `mode="following"`, optional when `mode="global"`).
- **Status Codes:**
  - `HTTP 200 OK`: Successful feed retrieval.
  - `HTTP 401 Unauthorized`: When `mode="following"` is requested without authentication.
  - `HTTP 422 Unprocessable Entity`: Invalid query parameters (limit out of range, negative offset).
- **Response Body (`FeedResponse`):**
  - `total` (`int`): Total count of matching posts across the feed window.
  - `limit` (`int`): Active limit parameter.
  - `offset` (`int`): Active offset parameter.
  - `items` (`list[FeedPostOut]`): Chronologically ordered posts (newest first). Each item includes author details (`id`, `username`, `avatar_url`), caption, image URL, media type, and optional linked recipe summary.

## Acceptance Criteria
1. Unauthenticated requests to `GET /api/v1/feed?mode=following` return HTTP 401.
2. Authenticated requests from a user who follows nobody return HTTP 200 with an empty list (`items: []`, `total: 0`).
3. When a user follows other creators, `mode="following"` returns posts authored by followed users and strictly excludes posts from unfollowed users.
4. Posts are delivered in reverse chronological order (`created_at DESC`, `id DESC`).
5. Pagination parameters (`limit` and `offset`) accurately paginate the timeline window and total counts.
6. Public requests to `GET /api/v1/feed?mode=global` return all community posts without requiring authentication.
7. All 6 automated tests in `backend/tests/test_feed.py` pass cleanly.
