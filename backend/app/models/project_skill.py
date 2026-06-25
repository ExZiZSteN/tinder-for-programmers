from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.skill import Skill


class ProjectSkill(Base):
    """Связующая таблица между проектами и навыками/технологиями"""
    __tablename__ = "project_skills"

    project_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    )
    skill_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    project: Mapped["Project"] = relationship(
        back_populates="project_skills",
        lazy="joined",
    )
    skill: Mapped["Skill"] = relationship(
        back_populates="project_skills",
        lazy="joined",
    )