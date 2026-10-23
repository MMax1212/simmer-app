from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, field_validator


class RequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


# --- US1.1: User Account Registration & Login (Registration Payload) ---
class UserCreate(RequestModel):
    email: EmailStr = Field(max_length=100)
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(min_length=8, max_length=1024)


# --- US1.1: User Account Registration & Login (Login Payload) ---
class LoginRequest(RequestModel):
    username_or_email: str = Field(min_length=1, max_length=100)
    password: str = Field(max_length=1024)


# --- US1.3: User Profile Management (Profile Update Payload) ---
class ProfileUpdate(RequestModel):
    bio: str | None = Field(default=None, max_length=500)
    avatar_url: str | None = Field(default=None, max_length=255)
    culinary_preferences: list[str] | None = Field(default=None, max_length=30)

    @field_validator("avatar_url")
    @classmethod
    def valid_avatar(cls, value: str | None) -> str | None:
        return str(HttpUrl(value)) if value else None

    @field_validator("culinary_preferences")
    @classmethod
    def valid_preferences(cls, values: list[str] | None) -> list[str]:
        if values is None:
            return []
        if any(not value.strip() or len(value.strip()) > 50 for value in values):
            raise ValueError("Preferences must contain 1 to 50 characters")
        return sorted({value.strip() for value in values})


# --- US1.3: User Profile Management (Public Profile Response) ---
class UserPublic(BaseModel):
    """Public lookup deliberately excludes private email and administrative fields."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    bio: str | None
    avatar_url: str | None
    culinary_preferences: list[str]
    created_at: datetime


# --- US1.1 & US1.2: Authenticated & Admin Profile Response ---
class UserPrivate(UserPublic):
    email: EmailStr
    role: Literal["user", "admin"]
    is_active: bool


# --- US1.1: User Account Registration & Login (JWT Token Response) ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPrivate


# --- US1.2: Admin Account & RBAC (Admin Status/Role Update Payload) ---
class AdminUserUpdate(RequestModel):
    is_active: bool | None = None
    role: Literal["user", "admin"] | None = None

    @field_validator("is_active", "role")
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("Use a concrete status or role")
        return value
