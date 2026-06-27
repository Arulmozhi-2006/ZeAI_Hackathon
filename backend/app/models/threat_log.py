import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Float, ForeignKey, Enum, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, UUIDPKMixin


class SeverityLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ThreatLog(Base, UUIDPKMixin):
    __tablename__ = "threat_logs"

    prompt_log_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("prompt_logs.id", ondelete="CASCADE"), nullable=False
    )
    threat_category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("threat_categories.id"), nullable=False
    )
    severity: Mapped[SeverityLevel] = mapped_column(
        Enum(SeverityLevel, name="severity_level"), nullable=False
    )
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    prompt_log = relationship("PromptLog", back_populates="threat_logs")
    threat_category = relationship("ThreatCategory", back_populates="threat_logs")