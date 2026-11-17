"""Criação do engine e das sessões do banco."""

from collections.abc import Callable

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base


DEFAULT_DATABASE_URL = "sqlite:///./anima_hub.db"


def create_database(database_url: str = DEFAULT_DATABASE_URL) -> Engine:
    """Cria o engine e as tabelas conhecidas pela aplicação."""
    # Importa os modelos antes do create_all para registrá-los no metadata.
    import app.models  # noqa: F401

    engine = create_engine(database_url, future=True)
    Base.metadata.create_all(engine)
    return engine


def create_session_factory(engine: Engine) -> Callable[[], Session]:
    """Retorna uma fábrica de sessões vinculada ao engine informado."""
    return sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
