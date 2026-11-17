"""Sincronização manual das fontes e persistência dos concursos."""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.ai.normalizer import FakeCompetitionNormalizer, OpenRouterCompetitionNormalizer
from app.models.competition import Competition
from app.models.profile import Profile
from app.repositories.competition import CompetitionRepository
from app.sources.errors import ConcursoSourceError
from app.sources.fake import FakeConcursoSource
from app.sources.real import ApiConcursoSource


@dataclass
class SyncResult:
    source: str
    states: list[str]
    found: int = 0
    details_processed: int = 0
    skipped: int = 0
    errors: list[str] | None = None
    sources: list[str] | None = None


def sync_competitions(session: Session, source_name: str, states: list[str]) -> SyncResult:
    source_names = ["real", "fake"] if source_name == "both" else [source_name]
    result = SyncResult(source=source_name, states=states, errors=[], sources=source_names)
    repository = CompetitionRepository(session)
    for current_source in source_names:
        source = FakeConcursoSource() if current_source == "fake" else ApiConcursoSource()
        try:
            for state in states:
                try:
                    listings = source.list_concursos(state)
                except ConcursoSourceError as error:
                    result.errors.append(f"{current_source}/{state}: {error}")
                    continue
                result.found += len(listings)
                for listing in listings:
                    repository.save_listing(listing)
                    try:
                        details = source.get_details(listing.source_url)
                        repository.save_details(details)
                        result.details_processed += 1
                    except (ConcursoSourceError, KeyError, ValueError) as error:
                        result.skipped += 1
                        result.errors.append(f"{listing.source_url}: {error}")
            session.commit()
        finally:
            close = getattr(source, "close", None)
            if close:
                close()
    return result


def list_competitions(session: Session) -> list[Competition]:
    return session.query(Competition).order_by(Competition.last_seen_at.desc()).all()
