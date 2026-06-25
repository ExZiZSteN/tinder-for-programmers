from datetime import datetime
import enum
from typing import TYPE_CHECKING,Optional
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.models.base import Base, TimestampMixin
if TYPE_CHECKING:
    from app.models.project_skill import ProjectSkill
    from app.models.skill import Skill
    from app.models.user import User
    from app.models.swipe import Swipe
    from app.models.project_member import ProjectMember

class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    COMPLETED = "completed"
    ARCHIVED = "archived"

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
    status: Mapped[ProjectStatus] = mapped_column(
        SQLEnum(ProjectStatus, name="project_status"),
        nullable=False,
        default=ProjectStatus.DRAFT,
        index=True
        )

    embedding: Mapped[Optional[list[float]]] = mapped_column(Vector(384), nullable=True)

    swipes: Mapped[list["Swipe"]] = relationship(
        back_populates="project",
        lazy="selectin",
    )
    project_skills: Mapped[list["ProjectSkill"]] = relationship(
        back_populates="project",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    owner: Mapped["User"] = relationship(back_populates="owned_projects", lazy="selectin")
    skills: Mapped[list["Skill"]] = relationship(
        secondary="project_skills", back_populates="projects", lazy="selectin"
    )
    members: Mapped[list["ProjectMember"]] = relationship(
        back_populates="project",
        lazy="selectin",
    )