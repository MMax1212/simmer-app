from pydantic import BaseModel, ConfigDict


# --- US1.2: Admin Account & RBAC (US-1.2-T-2: Admin System Metrics Response DTO) ---
class AdminStatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_users: int
    active_users: int
    deactivated_users: int
    admin_users: int
    total_posts: int
    total_recipes: int

