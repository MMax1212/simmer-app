from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUser, DbSession
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.schemas.user import LoginRequest, Token, UserCreate, UserPrivate

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserPrivate, status_code=status.HTTP_201_CREATED)
def register(body: UserCreate, db: DbSession):
    email = body.email.lower()
    existing = db.scalar(select(User).where(or_(User.email == email, func.lower(User.username) == body.username.lower())))
    if existing:
        raise HTTPException(status_code=409, detail="Username or email already registered")
    user = User(email=email, username=body.username, hashed_password=hash_password(body.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Username or email already registered")
    db.refresh(user)
    return user


def _authenticate(db: DbSession, identifier: str, password: str) -> Token:
    identifier = identifier.strip().lower()
    user = db.scalar(select(User).where(or_(User.email == identifier, func.lower(User.username) == identifier)))
    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username/email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    # Preserve existing bcrypt accounts and upgrade their hash on successful login.
    if user.hashed_password.startswith("$2"):
        user.hashed_password = hash_password(password)
        db.commit()
    return Token(access_token=create_access_token(user.id), user=UserPrivate.model_validate(user))


@router.post("/login", response_model=Token)
def login(body: LoginRequest, db: DbSession):
    return _authenticate(db, body.username_or_email, body.password)


@router.post("/token", response_model=Token, include_in_schema=False)
def login_form(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession):
    return _authenticate(db, form.username, form.password)


@router.get("/me", response_model=UserPrivate)
def read_me(user: CurrentUser):
    return user
