import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, Text, ForeignKey, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, UUIDPKMixin


class DecisionType(str, enum.Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"


class FirewallDecision(Base, UUIDPKMixin):
    __tablename__ = "firewall_decisions"

    prompt_log_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("prompt_logs.id", ondelete="CASCADE"), nullable=False
    )
    detection_result_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("detection_results.id", ondelete="CASCADE"), nullable=True
    )
    decision: Mapped[DecisionType] = mapped_column(Enum(DecisionType, name="decision_type"), nullable=False)
    policy_rule_triggered: Mapped[str] = mapped_column(String(255), nullable=True)
    decision_reason: Mapped[str] = mapped_column(Text, nullable=True)
    llm_provider: Mapped[str] = mapped_column(String(50), nullable=True)
    llm_forwarded: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    prompt_log = relationship("PromptLog", back_populates="firewall_decisions")
    detection_result = relationship("DetectionResult", back_populates="firewall_decision")