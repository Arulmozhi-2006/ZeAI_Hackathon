import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.analytics import OverviewStats, ModelMetrics
from app.services.analytics_service import (
    get_overview, get_category_breakdown, get_severity_breakdown,
    get_trends, get_model_metrics,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])  # ← MUST HAVE THIS
logger = logging.getLogger(__name__)


def _scope_user_id(current_user: User):
    if current_user.role in (UserRole.ADMIN, UserRole.ANALYST):
        return None
    return current_user.id


@router.get("/overview", response_model=OverviewStats)
def overview(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_overview(db, _scope_user_id(current_user), days)


@router.get("/categories")
def categories(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_category_breakdown(db, _scope_user_id(current_user), days)


@router.get("/severity")
def severity(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_severity_breakdown(db, _scope_user_id(current_user), days)


@router.get("/trends")
def trends(
    days: int = Query(14, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_trends(db, _scope_user_id(current_user), days)