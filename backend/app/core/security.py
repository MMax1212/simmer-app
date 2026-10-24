from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError

from app.core.config import settings

# --- US1.1: User Account Registration & Login (Password Hashing & JWT Security) ---
password_hasher = PasswordHasher()

# Hashes test using Argon2 algo 
def hash_password(password: str) -> str:
    return password_hasher.hash(password)

# verifies [assword matched the existing password hash
def verify_password(password: str, hashed: str) -> bool:
    try:
        if hashed.startswith("$2"):
            return len(password.encode()) <= 72 and bcrypt.checkpw(password.encode(), hashed.encode())
        return password_hasher.verify(hashed, password)
    except (VerificationError, InvalidHashError, ValueError):
        return False

# Generates a JWT access token for authentication
def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": str(user_id), "exp": expire}, settings.secret_key, algorithm=settings.algorithm)

# validates incoming JWT and retireves authenticated user ID
def decode_access_token(token: str) -> int | None:
    """Return the user id inside a valid token, or None if invalid/expired."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError, TypeError):
        return None
