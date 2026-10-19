from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, or_, select

from app.api.deps import DbSession
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.schemas.user import LoginRequest, Token, UserCreate, UserPrivate

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserPrivate, status_code=status.HTTP_201_CREATED)
def register(body: UserCreate, db: DbSession):
    """US1.1: create an account. Emails and usernames are unique (case-insensitive)."""
    email = body.email.lower()
    existing = db.scalar(
        select(User).where(or_(User.email == email, func.lower(User.username) == body.username.lower()))
    )
    if existing:
        field = "Email" if existing.email == email else "Username"
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{field} is already taken")

    user = User(email=email, username=body.username, hashed_password=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _authenticate(db: DbSession, email: str, password: str) -> Token:
    user = db.scalar(select(User).where(User.email == email.lower()))
    # Same message for "no such user" and "wrong password" so attackers can't probe emails.
    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")
    return Token(access_token=create_access_token(user.id))


@router.post("/login", response_model=Token)
def login(body: LoginRequest, db: DbSession):
    """JSON login used by the React app."""
    return _authenticate(db, body.email, body.password)


@router.post("/token", response_model=Token, include_in_schema=False)
def login_form(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession):
    """Form login used only by the Swagger 'Authorize' button. Put your email in 'username'."""
    return _authenticate(db, form.username, form.password)
