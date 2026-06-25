from datetime import datetime
from typing import Optional
import enum
from sqlalchemy import BigInteger, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from app.models.swipe import Swipe
from app.models.user import User
from app.models.user import Project

class MatchStatus(str, enum.Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    COMPLETED = "complited"

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
    status: Mapped[str] = mapped_column(
        SQLEnum(MatchStatus, name="match_status"), 
        nullable=False,
        default=MatchStatus.ACTIVE
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    closed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    user: Mapped["User"] = relationship(lazy="selectin")
    project: Mapped["Project"] = relationship(lazy="selectin")
    swipe: Mapped["Swipe"] = relationship(lazy="selectin")
    __table_args__ = (
        UniqueConstraint("user_id", "project_id", name="uq_match_pair"),
    )