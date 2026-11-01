from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MVPMilestone(Base):
    __tablename__ = "mvp_milestones"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    founder_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    startup_id: Mapped[int] = mapped_column(
        ForeignKey(
            "startups.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    mvp_plan_id: Mapped[int] = mapped_column(
        ForeignKey(
            "mvp_plans.id",
            ondelete="CASCADE"
        ),
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

    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="NOT_STARTED",
        nullable=False
    )

    target_days: Mapped[int] = mapped_column(
        Integer,
        default=7,
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