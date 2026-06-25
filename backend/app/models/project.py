from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.skill import Skill
    from app.models.user import User
    from app.models.project_member import ProjectMember
    from app.models.project_skill import ProjectSkill


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    format: Mapped[str] = mapped_column(String(20), nullable=False, default="remote")
    payment_type: Mapped[str] = mapped_column(String(20), nullable=False, default="volunteer")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", index=True)

    embedding: Mapped[Optional[list[float]]] = mapped_column(Vector(384), nullable=True)

    # Relationships
    owner: Mapped["User"] = relationship(back_populates="owned_projects", lazy="selectin")
    skills: Mapped[list["Skill"]] = relationship(
        secondary="project_skills", back_populates="projects", lazy="selectin"
    )
    members: Mapped[list["ProjectMember"]] = relationship(
        back_populates="project",
        lazy="selectin",
        passive_deletes=True,
    )
    project_skills: Mapped[list["ProjectSkill"]] = relationship(
        back_populates="project",
        lazy="selectin",
        passive_deletes=True,
    )