from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Text, func, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.match import Match
    from app.models.user import User


class Message(Base):
    __tablename__ = "messages"

    __table_args__ = (
        CheckConstraint(
            "char_length(content) BETWEEN 1 AND 4000", 
            name="chk_message_content"
        ),
        Index("idx_messages_match_created", "match_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    
    match_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("matches.id", ondelete="CASCADE"),
        nullable=False
    )
    
    sender_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False
    )
    
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    match: Mapped["Match"] = relationship(back_populates="messages", lazy="selectin")
    sender: Mapped["User"] = relationship(back_populates="sent_messages", lazy="selectin")
