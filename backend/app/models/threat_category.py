from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class ThreatCategory(Base):
    __tablename__ = "threat_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    default_severity: Mapped[str] = mapped_column(String(20), nullable=False, default="LOW")

    model_predictions = relationship("ModelPrediction", back_populates="predicted_category")
    detection_results = relationship("DetectionResult", back_populates="final_category")
    threat_logs = relationship("ThreatLog", back_populates="threat_category")