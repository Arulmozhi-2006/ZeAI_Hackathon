from datetime import date as date_type

from sqlalchemy import Date, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class AnalyticsDaily(Base):
    __tablename__ = "analytics_daily"

    date: Mapped[date_type] = mapped_column(Date, primary_key=True)
    total_requests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_allowed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_blocked: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    top_category_id: Mapped[int] = mapped_column(Integer, nullable=True)
    avg_risk_score: Mapped[float] = mapped_column(Float, nullable=True)
    avg_confidence_score: Mapped[float] = mapped_column(Float, nullable=True)