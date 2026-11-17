"""Perfil único do MVP."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    education_level: Mapped[str] = mapped_column(String(40), nullable=False)
    education: Mapped[str] = mapped_column(String(300), nullable=False)
    target_positions: Mapped[str] = mapped_column(Text, default="", nullable=False)
    knowledge_areas: Mapped[str] = mapped_column(Text, default="", nullable=False)
    experience: Mapped[str] = mapped_column(Text, default="", nullable=False)
    minimum_salary: Mapped[float | None] = mapped_column()
    states: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
