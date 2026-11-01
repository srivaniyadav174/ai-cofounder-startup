from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class GrowthAssessment(Base):
    __tablename__ = "growth_assessments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    founder_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    startup_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("startups.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # ========================================================
    # BUSINESS METRICS
    # ========================================================

    monthly_revenue: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    monthly_customers: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    monthly_growth_percentage: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    conversion_rate_percentage: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    retention_rate_percentage: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    churn_rate_percentage: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    average_revenue_per_customer: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    # ========================================================
    # BUSINESS CONTEXT
    # ========================================================

    acquisition_channels: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    pricing_model: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    sales_process: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    competitive_landscape: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    current_challenges: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    growth_goal: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # ========================================================
    # AI DIAGNOSIS
    # ========================================================

    growth_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    primary_bottleneck: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True
    )

    root_causes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    growth_opportunities: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    recommendations: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    action_plan: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # ========================================================
    # STATUS
    # ========================================================

    status: Mapped[str] = mapped_column(
        String(50),
        default="ASSESSED",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )