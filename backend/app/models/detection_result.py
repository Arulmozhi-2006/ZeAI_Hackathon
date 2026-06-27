import uuid
from datetime import datetime

from sqlalchemy import Float, Text, ForeignKey, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, UUIDPKMixin


class DetectionResult(Base, UUIDPKMixin):
    __tablename__ = "detection_results"

    prompt_log_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("prompt_logs.id", ondelete="CASCADE"), nullable=False
    )
    model_prediction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("model_predictions.id", ondelete="CASCADE"), nullable=False
    )
    final_category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("threat_categories.id"), nullable=False
    )
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    classification_reason: Mapped[str] = mapped_column(Text, nullable=True)
    threat_explanation: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    prompt_log = relationship("PromptLog", back_populates="detection_results")
    model_prediction = relationship("ModelPrediction", back_populates="detection_results")
    final_category = relationship("ThreatCategory", back_populates="detection_results")
    firewall_decision = relationship("FirewallDecision", back_populates="detection_result", uselist=False)