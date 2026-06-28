import uuid
from datetime import datetime

from sqlalchemy import String, Float, ForeignKey, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, UUIDPKMixin


class ModelPrediction(Base, UUIDPKMixin):
    __tablename__ = "model_predictions"

    prompt_log_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("prompt_logs.id", ondelete="CASCADE"), nullable=False
    )
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    embedding_vector: Mapped[dict] = mapped_column(JSONB, nullable=True)
    predicted_category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("threat_categories.id"), nullable=False
    )
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    raw_model_output: Mapped[dict] = mapped_column(JSONB, nullable=True)
    inference_time_ms: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    prompt_log = relationship("PromptLog", back_populates="model_predictions")
    predicted_category = relationship("ThreatCategory", back_populates="model_predictions")
    detection_results = relationship("DetectionResult", back_populates="model_prediction")