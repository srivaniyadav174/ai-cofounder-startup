from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ValidationExperiment(Base):
    __tablename__ = "validation_experiments"

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

    title: Mapped[str] = mapped_column(
        String(250),
        nullable=False
    )

    hypothesis: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    experiment_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    success_criteria: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="PLANNED",
        nullable=False
    )

    result: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    learning: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    next_action: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        default=1,
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