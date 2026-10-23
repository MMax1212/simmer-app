from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class UserCreate(RequestModel):
    email: EmailStr = Field(max_length=100)
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(min_length=8, max_length=1024)


class LoginRequest(RequestModel):
    username_or_email: str = Field(min_length=1, max_length=100)
    password: str = Field(max_length=1024)


class UserPrivate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    role: Literal["user", "admin"]
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPrivate


class AdminUserUpdate(RequestModel):
    is_active: bool | None = None
    role: Literal["user", "admin"] | None = None

    @field_validator("is_active", "role")
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("Use a concrete status or role")
        return value
