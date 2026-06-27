import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit_trail import AuditTrail

logger = logging.getLogger(__name__)


def log_action(
    db: Session,
    action_type: str,
    user_id: Optional[UUID] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> None:
    entry = AuditTrail(
        user_id=user_id,
        action_type=action_type,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id else None,
        ip_address=ip_address,
        metadata_json=metadata or {},
    )
    db.add(entry)
    db.commit()