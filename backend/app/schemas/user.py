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