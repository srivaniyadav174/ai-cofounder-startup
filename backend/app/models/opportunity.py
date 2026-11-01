from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Opportunity(Base):
    __tablename__ = "opportunities"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    founder_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(250),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    industry: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )

    required_skills: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    required_experience: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    target_customers: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    business_model: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    estimated_investment: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    difficulty: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    market_potential: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    founder_fit_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    why_it_fits: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    risks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    recommended_next_step: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )