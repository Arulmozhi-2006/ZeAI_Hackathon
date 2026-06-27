from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class APIKeyCreate(BaseModel):
    name: str
    scopes: dict = {}
    expires_at: Optional[datetime] = None


class APIKeyRead(BaseModel):
    id: UUID
    name: str
    key_prefix: str
    scopes: dict
    is_active: bool
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class APIKeyCreated(APIKeyRead):
    """Returned only on creation — includes the raw key."""
    raw_key: str