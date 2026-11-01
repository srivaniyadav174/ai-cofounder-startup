from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MVPTask(Base):
    __tablename__ = "mvp_tasks"

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

    mvp_plan_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("mvp_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    milestone_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "mvp_milestones.id",
            ondelete="SET NULL"
        ),
        nullable=True,
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

    priority: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )

    estimated_hours: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="TODO",
        nullable=False
    )

    due_days: Mapped[int | None] = mapped_column(
        Integer,
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