import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.api_key import APIKeyCreate, APIKeyRead, APIKeyCreated
from app.schemas.auth import TokenResponse, RefreshRequest, LoginRequest
from app.schemas.user import UserCreate, UserRead
from app.services.auth_service import (
    create_user, authenticate_user, build_token_response,
    refresh_access_token, create_api_key, list_api_keys, revoke_api_key,
)

router = APIRouter(prefix="/auth", tags=["auth"])  # ← MUST HAVE THIS
logger = logging.getLogger(__name__)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    try:
        user = create_user(db, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return build_token_response(user)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return build_token_response(user)


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    try:
        return refresh_access_token(db, data.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user


# ── API Keys ─────────────────────────────────────────────────────────────────

@router.post("/api-keys", response_model=APIKeyCreated, status_code=status.HTTP_201_CREATED)
def create_key(data: APIKeyCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    key, raw = create_api_key(db, current_user, data.name, data.scopes, data.expires_at)
    return APIKeyCreated(
        id=key.id, name=key.name, key_prefix=key.key_prefix,
        scopes=key.scopes, is_active=key.is_active,
        last_used_at=key.last_used_at, expires_at=key.expires_at,
        created_at=key.created_at, raw_key=raw,
    )


@router.get("/api-keys", response_model=list[APIKeyRead])
def get_keys(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return list_api_keys(db, current_user)


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_key(key_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from uuid import UUID
    if not revoke_api_key(db, UUID(key_id), current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")