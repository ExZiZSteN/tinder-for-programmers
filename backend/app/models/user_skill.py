from datetime import datetime
from sqlalchemy import BigInteger, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from app.models.user import User
from app.models.skill import Skill

class UserSkill(Base):
    """Связующая таблица между пользователями и навыками"""
    __tablename__ = "user_skills"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    skill_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    user: Mapped["User"] = relationship(
        back_populates="user_skills",
        lazy="joined",
    )
    skill: Mapped["Skill"] = relationship(
        back_populates="user_skills",
        lazy="joined",
    )