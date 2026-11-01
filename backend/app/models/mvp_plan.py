from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MVPPlan(Base):
    __tablename__ = "mvp_plans"

    __table_args__ = (
        UniqueConstraint(
            "startup_id",
            name="uq_mvp_plan_startup"
        ),
    )

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

    validation_decision_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "validation_decisions.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(250),
        nullable=False
    )

    objective: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    problem_to_solve: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    target_customer: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    core_value_proposition: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    scope: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    out_of_scope: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    success_metrics: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    estimated_duration_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="PLANNED",
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