import base64
import hashlib
import hmac
import os
import time
from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User

TOKEN_SECRET = os.getenv("MINDPATH_TOKEN_SECRET", "mindpath-local-secret")
TOKEN_TTL_SECONDS = 60 * 60 * 24


@dataclass(frozen=True)
class AuthResult:
    user: User
    access_token: str


class AuthService:
    @staticmethod
    def normalize_email(email: str) -> str:
        return email.strip().lower()

    @staticmethod
    def hash_password(password: str) -> str:
        salt = os.urandom(16)
        password_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, 120_000
        )
        return f"{base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(password_hash).decode()}"

    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        try:
            salt_text, hash_text = stored_hash.split("$", 1)
            salt = base64.urlsafe_b64decode(salt_text.encode())
            expected = base64.urlsafe_b64decode(hash_text.encode())
            actual = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt, 120_000
            )
            return hmac.compare_digest(actual, expected)
        except ValueError:
            return False

    @staticmethod
    def create_token(user: User) -> str:
        expires_at = int(time.time()) + TOKEN_TTL_SECONDS
        payload = f"{user.id}:{user.email}:{expires_at}"
        signature = hmac.new(
            TOKEN_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        raw_token = f"{payload}:{signature}"
        return base64.urlsafe_b64encode(raw_token.encode("utf-8")).decode("utf-8")

    @staticmethod
    async def get_user_from_token(db: AsyncSession, token: str) -> User | None:
        try:
            decoded = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
            user_id_text, email, expires_at_text, signature = decoded.rsplit(":", 3)
            payload = f"{user_id_text}:{email}:{expires_at_text}"
            expected_signature = hmac.new(
                TOKEN_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(signature, expected_signature):
                return None
            if int(expires_at_text) < int(time.time()):
                return None
            user_id = int(user_id_text)
        except (ValueError, UnicodeDecodeError):
            return None

        return await db.get(User, user_id)

    @staticmethod
    async def register(db: AsyncSession, email: str, password: str) -> AuthResult:
        normalized_email = AuthService.normalize_email(email)
        if "@" not in normalized_email or "." not in normalized_email:
            raise HTTPException(status_code=400, detail="Enter a valid email address")

        existing_user = await db.scalar(select(User).where(User.email == normalized_email))
        if existing_user is not None:
            raise HTTPException(status_code=400, detail="Email is already registered")

        user = User(
            email=normalized_email,
            password_hash=AuthService.hash_password(password),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return AuthResult(user=user, access_token=AuthService.create_token(user))

    @staticmethod
    async def login(db: AsyncSession, email: str, password: str) -> AuthResult:
        normalized_email = AuthService.normalize_email(email)
        user = await db.scalar(select(User).where(User.email == normalized_email))
        if user is None or not AuthService.verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        return AuthResult(user=user, access_token=AuthService.create_token(user))
