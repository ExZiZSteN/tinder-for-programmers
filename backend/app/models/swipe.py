from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, UniqueConstraint, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User

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
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    project: Mapped["Project"] = relationship(back_populates="swipes", lazy="selectin")
    user: Mapped["User"] = relationship(back_populates="swipes", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("user_id", "project_id", name="uq_swipe_per_project"),
        Index("idx_swipe_project_status", "project_id", "status"),
    )