from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.runtime import get_session
from app.main import app
from app.models.profile import Profile
from app.repositories.competition import CompetitionRepository
from app.sources.fake import FakeConcursoSource


def test_recommendations_only_return_profile_states() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)

    with factory() as session:
        session.add(
            Profile(
                id=1,
                name="Teste",
                education_level="superior",
                education="Tecnologia",
                target_positions="Analista",
                knowledge_areas="tecnologia",
                experience="programação",
                minimum_salary=None,
                states=["PE"],
                description="",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
        )
        source = FakeConcursoSource()
        repository = CompetitionRepository(session)
        for state in ("CE", "PE"):
            listing = source.list_concursos(state)[0]
            repository.save_listing(listing)
            repository.save_details(source.get_details(listing.source_url))
        session.commit()

    def override_session():
        with factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    try:
        response = TestClient(app).get("/recomendacoes")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()
    assert {item["state"] for item in response.json()} == {"PE"}
