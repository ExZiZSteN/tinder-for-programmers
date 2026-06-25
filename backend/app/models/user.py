from sqlalchemy import String, DateTime, func, Boolean, BigInteger, Text, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from pgvector.sqlalchemy import Vector
from app.models.base import Base, TimestampMixin
from app.models.skill import Skill
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user_skill import UserSkill
from typing import Optional
from datetime import datetime

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger,primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False, index=True)
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

    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(),
        nullable=False
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