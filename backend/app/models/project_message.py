from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import BigInteger, DateTime, ForeignKey, Text, CheckConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User


class ProjectMessage(Base):
    __tablename__ = "project_messages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sender_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    project: Mapped["Project"] = relationship(lazy="selectin")
    sender: Mapped["User"] = relationship(lazy="selectin")

    __table_args__ = (
        CheckConstraint("LENGTH(content) <= 4000", name="chk_project_message_content_length"),
        Index("idx_project_messages_project_created", "project_id", "created_at"),
    )