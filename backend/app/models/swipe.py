from enum import Enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import BigInteger, DateTime, ForeignKey, Text, UniqueConstraint, func, Index
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User
    from app.models.match import Match


class SwipeStatus(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"
    WITHDRAWN = "withdrawn"


class Swipe(Base):
    __tablename__ = "swipes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    project_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[SwipeStatus] = mapped_column(
        SQLEnum(
            SwipeStatus,
            name="swipe_status",
            create_constraint=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=SwipeStatus.PENDING,
    )
    match_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("matches.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    project: Mapped["Project"] = relationship(back_populates="swipes", lazy="selectin")
    user: Mapped["User"] = relationship(back_populates="swipes", lazy="selectin")
    match: Mapped[Optional["Match"]] = relationship(
        lazy="selectin",
        foreign_keys=[match_id],
    )

    __table_args__ = (
        UniqueConstraint("user_id", "project_id", name="uq_swipe_per_project"),
        Index("idx_swipe_project_status", "project_id", "status"),
    )