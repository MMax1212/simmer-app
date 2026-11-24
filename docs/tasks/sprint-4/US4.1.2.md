---
id: US4.1.2
story: US4.1
sprint: 4
assignee: Bryan Moreno
estimate_hours: 3
---

# Add Relationship Status and Follower Counts to User Search DTOs

## Description
Serves **US4.1** (*Friend Search & Network*). When users search for friends or browse user directories, they need immediate contextual relationship feedback:
1. Whether they already follow each user in the results (`is_following: boolean`).
2. The user's social proof and network metrics (`followers_count: int` and `following_count: int`).

To ensure high performance and prevent $N+1$ query overhead on large search queries, this task implements batch aggregation:
- Follower count lookup via `group_by(UserFollow.following_id)`.
- Following count lookup via `group_by(UserFollow.follower_id)`.
- Caller follow relationship lookup via single `UserFollow.follower_id == current_user.id` set filter.

## DTO Specification (`UserSearchResultItem`)
```python
class UserSearchResultItem(BaseModel):
    id: int
    username: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    culinary_preferences: Optional[List[str]] = None
    created_at: datetime
    is_following: bool = False
    followers_count: int = 0
    following_count: int = 0
```

## Acceptance Criteria
1. When caller is unauthenticated, `is_following` defaults to `False` for all returned users.
2. When caller is authenticated, `is_following` is `True` if and only if an active `UserFollow` record exists where `follower_id = current_user.id` and `following_id = result.id`.
3. `followers_count` accurately reflects the total number of followers following that user.
4. `following_count` accurately reflects the total number of users that user is following.
5. All counts and relationship states are fetched via batch queries without $N+1$ query degradation.
6. Automated integration tests in `backend/tests/test_user_search.py` verify accuracy across followed and unfollowed users.
