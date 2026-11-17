"""Sessão compartilhada pelas rotas durante a execução da API."""

from collections.abc import Generator

from app.db.database import create_database, create_session_factory

engine = create_database()
SessionLocal = create_session_factory(engine)


def get_session() -> Generator:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
