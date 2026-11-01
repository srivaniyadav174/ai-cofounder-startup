from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FounderProfile(Base):
    __tablename__ = "founder_profiles"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    # Basic information
    location: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    education: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )

    # Capabilities
    skills: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    experience: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    available_time: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    # Resources
    budget: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    team_status: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    # Preferences
    interests: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    preferred_industries: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    business_preference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    risk_tolerance: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    # Goals
    target_income: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    short_term_goal: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    long_term_goal: Mapped[str | None] = mapped_column(
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