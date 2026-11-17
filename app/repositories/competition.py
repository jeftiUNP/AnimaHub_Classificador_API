"""Persistência incremental dos dados extraídos de concursos."""

from datetime import datetime, timezone
from hashlib import sha256
import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.competition import Competition
from app.sources.contracts import ConcursoDetails, ConcursoListing


class CompetitionRepository:
    """Salva listagens e detalhes sem duplicar a mesma fonte e URL."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save_listing(self, listing: ConcursoListing, seen_at: datetime | None = None) -> Competition:
        """Insere ou atualiza um concurso observado na listagem."""
        now = seen_at or utc_now()
        source_url = str(listing.source_url)
        competition = self._find(listing.source, source_url)

        if competition is None:
            competition = Competition(
                source=listing.source,
                source_url=source_url,
                state=listing.state,
                organization=listing.organization,
                source_status=listing.source_status,
                vacancies_text=listing.vacancies_text,
                first_seen_at=now,
                last_seen_at=now,
                created_at=now,
                updated_at=now,
            )
            self.session.add(competition)
        else:
            competition.state = listing.state
            competition.organization = listing.organization
            competition.source_status = listing.source_status
            competition.vacancies_text = listing.vacancies_text
            competition.last_seen_at = now
            competition.updated_at = now

        self.session.flush()
        return competition

    def save_details(self, details: ConcursoDetails, processed_at: datetime | None = None) -> Competition:
        """Salva os detalhes normalizados e calcula seu hash de conteúdo."""
        now = processed_at or utc_now()
        source_url = str(details.source_url)
        competition = self._find(details.source, source_url)
        content_hash = calculate_content_hash(details)

        if competition is None:
            competition = Competition(
                source=details.source,
                source_url=source_url,
                state="??",
                organization=details.author or "Desconhecido",
                source_status="unknown",
                first_seen_at=now,
                last_seen_at=now,
                created_at=now,
                updated_at=now,
            )
            self.session.add(competition)

        competition.title = details.title
        competition.summary = details.summary
        competition.author = details.author
        competition.published_at = details.published_at
        competition.source_updated_at = details.updated_at
        competition.content = details.content
        competition.content_hash = content_hash
        competition.introduction = details.introduction
        competition.sections = [section.model_dump() for section in details.sections]
        competition.links = [link.model_dump(mode="json") for link in details.links]
        competition.details_processed_at = now
        competition.updated_at = now
        self.session.flush()
        return competition

    def _find(self, source: str, source_url: str) -> Competition | None:
        return self.session.scalar(
            select(Competition).where(
                Competition.source == source,
                Competition.source_url == source_url,
            )
        )


def calculate_content_hash(details: ConcursoDetails) -> str:
    """Gera hash estável para evitar reprocessar conteúdo idêntico."""
    payload = details.model_dump(mode="json", exclude={"source"})
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256(serialized.encode("utf-8")).hexdigest()


def utc_now() -> datetime:
    """Retorna UTC sem timezone para compatibilidade com SQLite local."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
