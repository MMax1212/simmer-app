from datetime import datetime

from pydantic import BaseModel, ConfigDict


# --- US1.2: Admin Account & RBAC (Audit Log Response DTO) ---
class AdminAuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    admin_id: int
    target_id: int
    before: dict
    after: dict
    created_at: datetime
