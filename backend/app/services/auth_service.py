import hashlib
import logging
import secrets
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.models.api_key import APIKey
from app.models.user import User, UserRole
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate

logger = logging.getLogger(__name__)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, data: UserCreate) -> User:
    if get_user_by_email(db, data.email):
        raise ValueError("Email already registered")
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        role="viewer",  # ← FIX: Use string value, not enum
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"Created user {user.email} ({user.id})")
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def build_token_response(user: User) -> TokenResponse:
    from app.schemas.user import UserRead
    access = create_access_token(str(user.id), {"role": user.role.value, "email": user.email})
    refresh = create_refresh_token(str(user.id))
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        user=UserRead.model_validate(user),
    )


def refresh_access_token(db: Session, refresh_token: str) -> TokenResponse:
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise ValueError("Invalid refresh token")
    user = get_user_by_id(db, UUID(payload["sub"]))
    if not user or not user.is_active:
        raise ValueError("User not found or inactive")
    return build_token_response(user)


# ── API Key helpers ──────────────────────────────────────────────────────────

def _hash_key(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def create_api_key(db: Session, user: User, name: str, scopes: dict, expires_at=None):
    raw = "fw_" + secrets.token_urlsafe(32)
    prefix = raw[:12]
    key = APIKey(
        user_id=user.id,
        key_hash=_hash_key(raw),
        key_prefix=prefix,
        name=name,
        scopes=scopes,
        expires_at=expires_at,
    )
    db.add(key)
    db.commit()
    db.refresh(key)
    return key, raw


def validate_api_key(db: Session, raw: str) -> Optional[APIKey]:
    from datetime import datetime, timezone
    h = _hash_key(raw)
    key = db.query(APIKey).filter(APIKey.key_hash == h, APIKey.is_active == True).first()
    if not key:
        return None
    if key.expires_at and key.expires_at < datetime.now(timezone.utc):
        return None
    key.last_used_at = datetime.now(timezone.utc)
    db.commit()
    return key


def list_api_keys(db: Session, user: User):
    return db.query(APIKey).filter(APIKey.user_id == user.id).all()


def revoke_api_key(db: Session, key_id: UUID, user: User) -> bool:
    key = db.query(APIKey).filter(APIKey.id == key_id, APIKey.user_id == user.id).first()
    if not key:
        return False
    key.is_active = False
    db.commit()
    return True