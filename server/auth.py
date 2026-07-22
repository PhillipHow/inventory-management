"""
Authentication for the Factory Inventory Management System.

Implements standards-compliant HS256 JWTs and PBKDF2 password verification
using only the Python standard library (no external dependencies). Demo users
are loaded from data/users.json via mock_data.

NOTE: SECRET_KEY defaults to a demo value. In production, set the
INVENTORY_JWT_SECRET environment variable to a strong random secret.
"""

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from mock_data import users as _users

# --- Configuration ---
SECRET_KEY = os.environ.get("INVENTORY_JWT_SECRET", "demo-secret-change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 8 * 60 * 60  # 8 hours

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Index users by username for quick lookup
_users_by_name = {u["username"]: u for u in _users}


# --- Models ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class User(BaseModel):
    username: str
    full_name: str
    role: str


# --- Base64url helpers ---
def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


# --- Password hashing (PBKDF2) ---
def verify_password(password: str, stored: str) -> bool:
    """Verify a plaintext password against a 'pbkdf2_sha256$iters$salt$hash' string."""
    try:
        algorithm, iterations, salt_hex, hash_hex = stored.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        dk = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt_hex), int(iterations)
        )
        return hmac.compare_digest(dk.hex(), hash_hex)
    except (ValueError, AttributeError):
        return False


# --- JWT (HS256) ---
def create_access_token(subject: str, role: str) -> str:
    header = {"alg": ALGORITHM, "typ": "JWT"}
    now = int(time.time())
    payload = {"sub": subject, "role": role, "iat": now, "exp": now + ACCESS_TOKEN_EXPIRE_SECONDS}
    segments = [
        _b64url_encode(json.dumps(header, separators=(",", ":")).encode()),
        _b64url_encode(json.dumps(payload, separators=(",", ":")).encode()),
    ]
    signing_input = ".".join(segments).encode()
    signature = hmac.new(SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
    segments.append(_b64url_encode(signature))
    return ".".join(segments)


def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT. Raises ValueError if invalid or expired."""
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
    except ValueError:
        raise ValueError("Malformed token")

    signing_input = f"{header_b64}.{payload_b64}".encode()
    expected = hmac.new(SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
    if not hmac.compare_digest(expected, _b64url_decode(signature_b64)):
        raise ValueError("Invalid signature")

    payload = json.loads(_b64url_decode(payload_b64))
    if payload.get("exp", 0) < int(time.time()):
        raise ValueError("Token expired")
    return payload


# --- Authentication logic ---
def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = _users_by_name.get(username)
    if not user or not verify_password(password, user["password_hash"]):
        return None
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
    except ValueError:
        raise credentials_exception

    username = payload.get("sub")
    user = _users_by_name.get(username)
    if user is None:
        raise credentials_exception
    return User(username=user["username"], full_name=user["full_name"], role=user["role"])
