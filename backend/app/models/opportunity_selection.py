from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class OpportunitySelection(Base):
    __tablename__ = "opportunity_selections"

    __table_args__ = (
        UniqueConstraint(
            "founder_id",
            name="uq_opportunity_selection_founder",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    founder_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    opportunity_id: Mapped[int] = mapped_column(
        ForeignKey(
            "opportunities.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    selection_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    selected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )