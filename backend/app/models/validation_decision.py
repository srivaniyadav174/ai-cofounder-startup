from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ValidationDecision(Base):
    __tablename__ = "validation_decisions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    founder_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    startup_id: Mapped[int] = mapped_column(
        ForeignKey("startups.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    decision: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    confidence_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    evidence_summary: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    strengths: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    weaknesses: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    key_learnings: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    recommendation: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    mvp_scope: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    next_actions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
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