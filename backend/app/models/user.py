from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, DateTime, func, Boolean, BigInteger, Text, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from pgvector.sqlalchemy import Vector
from datetime import datetime
from app.models.base import Base, TimestampMixin
if TYPE_CHECKING:
    from app.models.skill import Skill
    from app.models.project import Project
    from app.models.project_member import ProjectMember
    from app.models.user_skill import UserSkill

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger,primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    user_role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    github_url: Mapped[str] = mapped_column(String(255), nullable=True)
    linkedin_url: Mapped[str] = mapped_column(String(255), nullable=True)
    portfolio_url: Mapped[str] = mapped_column(String(255), nullable=True)
    experience_years: Mapped[int] = mapped_column(SmallInteger, default=0)
    avatar_file_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    resume_file_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    embedding: Mapped[Optional[list[float]]] = mapped_column(Vector(384), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    user_skills: Mapped[list["UserSkill"]] = relationship(
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    skills: Mapped[list["Skill"]] = association_proxy(
        "user_skills", "skill",
        creator=lambda skill: UserSkill(skill=skill),
    )
    owned_projects: Mapped[list["Project"]] = relationship(
        back_populates="owner", lazy="selectin"
    )
    project_memberships: Mapped[list["ProjectMember"]] = relationship(
        back_populates="user",
        lazy="selectin",
    )
    swipes: Mapped[list["Swipe"]] = relationship(
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    matches: Mapped[list["Match"]] = relationship(
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    sent_messages: Mapped[list["Message"]] = relationship(
        back_populates="sender",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    notifications: Mapped[list["Notification"]] = relationship(
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    files: Mapped[list["File"]] = relationship(
        back_populates="owner",
        lazy="selectin",
        cascade="all, delete-orphan",
    )