import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.logs import PromptLogRead, ThreatLogRead, DetectionDetailRead
from app.services.logs_service import get_prompt_logs, get_threat_logs, get_detection_detail

router = APIRouter(prefix="/logs", tags=["logs"])  # ← MUST HAVE THIS
logger = logging.getLogger(__name__)


def _scope_user_id(current_user: User) -> Optional[UUID]:
    """Admins/analysts see all rows; viewers see only their own."""
    if current_user.role in (UserRole.ADMIN, UserRole.ANALYST):
        return None
    return current_user.id


@router.get("/prompts")
def list_prompt_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = get_prompt_logs(db, _scope_user_id(current_user), page, page_size)
    return {
        "items": [PromptLogRead.model_validate(i) for i in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/threats")
def list_threat_logs(
    severity: Optional[str] = Query(None, pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = get_threat_logs(db, _scope_user_id(current_user), severity, page, page_size)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{prompt_log_id}", response_model=DetectionDetailRead)
def get_log_detail(
    prompt_log_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    detail = get_detection_detail(db, prompt_log_id, _scope_user_id(current_user))
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    return detail