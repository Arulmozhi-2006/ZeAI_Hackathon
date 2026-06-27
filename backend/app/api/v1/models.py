import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.analytics import ModelMetrics
from app.services.analytics_service import get_model_metrics

router = APIRouter(prefix="/models", tags=["models"])  # ← MUST HAVE THIS
logger = logging.getLogger(__name__)


@router.get("/metrics", response_model=ModelMetrics)
def model_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_model_metrics(db)