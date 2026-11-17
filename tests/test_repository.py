from datetime import datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models.competition import Competition
from app.repositories.competition import CompetitionRepository
from app.sources.fake import FakeConcursoSource


def test_repository_saves_listing_once_and_updates_last_seen() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    source = FakeConcursoSource()
    listing = source.list_concursos("CE")[0]
    first_seen = datetime(2026, 11, 8, 10, 0)
    second_seen = datetime(2026, 11, 8, 11, 0)

    with Session(engine) as session:
        repository = CompetitionRepository(session)
        competition = repository.save_listing(listing, seen_at=first_seen)
        repository.save_listing(listing, seen_at=second_seen)
        session.commit()

        rows = session.scalars(select(Competition)).all()
        assert len(rows) == 1
        assert rows[0].id == competition.id
        assert rows[0].first_seen_at == first_seen
        assert rows[0].last_seen_at == second_seen


def test_repository_saves_details_and_content_hash() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    source = FakeConcursoSource()
    listing = source.list_concursos("CE")[0]
    details = source.get_details(listing.source_url)

    with Session(engine) as session:
        repository = CompetitionRepository(session)
        competition = repository.save_listing(listing)
        repository.save_details(details)
        session.commit()
        session.refresh(competition)

        assert competition.title == details.title
        assert competition.content == details.content
        assert competition.content_hash is not None
        assert len(competition.content_hash) == 64
        assert competition.details_processed_at is not None
        assert competition.sections[0]["title"] == "Requisitos"
