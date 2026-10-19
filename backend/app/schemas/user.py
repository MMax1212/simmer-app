from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class DietaryPref(str, Enum):
    """Shared tag list: reuse this for recipe dietary tags in Sprint 4 (US4.4)."""

    vegetarian = "vegetarian"
    vegan = "vegan"
    pescatarian = "pescatarian"
    gluten_free = "gluten-free"
    dairy_free = "dairy-free"
    nut_free = "nut-free"
    halal = "halal"
    kosher = "kosher"
    low_carb = "low-carb"


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(min_length=8, max_length=72)  # bcrypt ignores bytes past 72


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProfileUpdate(BaseModel):
    """PATCH body: every field optional, only sent fields change."""

    bio: str | None = Field(default=None, max_length=500)
    avatar_url: str | None = Field(default=None, max_length=500)
    dietary_prefs: list[DietaryPref] | None = None


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    bio: str | None
    avatar_url: str | None
    dietary_prefs: list[str]
    created_at: datetime


class UserPrivate(UserPublic):
    """What a user sees about themselves (adds email and role)."""

    email: EmailStr
    role: str
    is_active: bool


class AdminUserUpdate(BaseModel):
    is_active: bool | None = None
    role: str | None = Field(default=None, pattern=r"^(user|admin)$")
