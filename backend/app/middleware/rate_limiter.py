"""
Simple sliding-window rate limiter backed by Postgres (no Redis, per constraints).
Counts requests per user/api-key within the last 60 seconds using audit_trail
ACTION_TYPE='FIREWALL_ANALYZE' rows. Lightweight enough for hackathon-scale traffic.
"""
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings

logger = logging.getLogger(__name__)


def check_rate_limit(db: Session, user_id: UUID) -> None:
    window_start = datetime.now(timezone.utc) - timedelta(minutes=1)
    count = db.execute(
        text(
            "SELECT COUNT(*) FROM audit_trail "
            "WHERE user_id = :uid AND action_type = 'FIREWALL_ANALYZE' "
            "AND created_at >= :window_start"
        ),
        {"uid": str(user_id), "window_start": window_start},
    ).scalar()

    if count is not None and count >= settings.RATE_LIMIT_PER_MINUTE:
        logger.warning(f"Rate limit exceeded for user {user_id}: {count} requests/min")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: {settings.RATE_LIMIT_PER_MINUTE} requests/min",
        )
