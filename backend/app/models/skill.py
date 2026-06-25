from typing import TYPE_CHECKING
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, func, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from app.models.base import Base
if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User
    from app.models.project_skill import ProjectSkill
    from app.models.user_skill import UserSkill


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    user_skills: Mapped[list["UserSkill"]] = relationship(
        back_populates="skill",
        lazy="selectin",
    )
    users: Mapped[list["User"]] = association_proxy(
        "user_skills", "user",
    )
    project_skills: Mapped[list["ProjectSkill"]] = relationship(
        back_populates="skill",
        lazy="selectin",
    )
    projects: Mapped[list["Project"]] = relationship(
        secondary="project_skills", back_populates="skills", lazy="selectin"
    )