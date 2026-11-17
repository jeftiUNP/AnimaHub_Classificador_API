"""Modelo persistido de concurso extraído de uma fonte."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Competition(Base):
    """Concurso encontrado na listagem e/ou nos detalhes da fonte."""

    __tablename__ = "competitions"
    __table_args__ = (UniqueConstraint("source", "source_url", name="uq_competition_source_url"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(80), nullable=False)
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    state: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    organization: Mapped[str] = mapped_column(String(300), nullable=False)
    title: Mapped[str | None] = mapped_column(String(500))
    source_status: Mapped[str] = mapped_column(String(40), nullable=False)
    normalized_status: Mapped[str] = mapped_column(
        String(40), nullable=False, default="DESCONHECIDO", server_default="DESCONHECIDO"
    )
    vacancies_text: Mapped[str | None] = mapped_column(String(100))
    summary: Mapped[str | None] = mapped_column(Text)
    author: Mapped[str | None] = mapped_column(String(200))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    content: Mapped[str | None] = mapped_column(Text)
    content_hash: Mapped[str | None] = mapped_column(String(64), index=True)
    introduction: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    sections: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    links: Mapped[list[dict[str, str]]] = mapped_column(JSON, nullable=False, default=list)
    raw_listing: Mapped[dict[str, object] | None] = mapped_column(JSON)
    raw_details: Mapped[dict[str, object] | None] = mapped_column(JSON)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    details_processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
