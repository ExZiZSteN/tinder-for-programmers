from datetime import datetime
from typing import TYPE_CHECKING, Optional
import enum
from sqlalchemy import BigInteger, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.project import Project
    from app.models.swipe import Swipe
    from app.models.message import Message


class MatchStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    REJECTED = "rejected"
    CLOSED = "closed"
    COMPLETED = "completed"


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    project_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("projects.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    swipe_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("swipes.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    status: Mapped[MatchStatus] = mapped_column(
        SQLEnum(
            MatchStatus,
            name="match_status",
            create_constraint=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=MatchStatus.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    closed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped["User"] = relationship(lazy="selectin")
    project: Mapped["Project"] = relationship(lazy="selectin")
    swipe: Mapped["Swipe"] = relationship(
        lazy="selectin",
        foreign_keys=[swipe_id],
    )
    messages: Mapped[list["Message"]] = relationship(
        back_populates="match",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "project_id", name="uq_match_pair"),
    )