from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Startup(Base):
    __tablename__ = "startups"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    founder_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    industry: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    stage: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    target_market: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    business_model: Mapped[str | None] = mapped_column(
        String(100),
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