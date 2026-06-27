import enum
import uuid

from sqlalchemy import String, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, UUIDPKMixin, TimestampMixin


class PromptStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    ERROR = "ERROR"


class PromptLog(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "prompt_logs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    api_key_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("api_keys.id", ondelete="SET NULL"), nullable=True
    )
    raw_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    source_ip: Mapped[str] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str] = mapped_column(String(500), nullable=True)
    status: Mapped[PromptStatus] = mapped_column(
        Enum(PromptStatus, name="prompt_status"), default=PromptStatus.PENDING, nullable=False
    )

    user = relationship("User", back_populates="prompt_logs")
    api_key = relationship("APIKey", back_populates="prompt_logs")
    model_predictions = relationship("ModelPrediction", back_populates="prompt_log", cascade="all, delete-orphan")
    detection_results = relationship("DetectionResult", back_populates="prompt_log", cascade="all, delete-orphan")
    firewall_decisions = relationship("FirewallDecision", back_populates="prompt_log", cascade="all, delete-orphan")
    threat_logs = relationship("ThreatLog", back_populates="prompt_log", cascade="all, delete-orphan")
    llm_responses = relationship("LLMResponse", back_populates="prompt_log", cascade="all, delete-orphan")