"""Base declarativa dos modelos SQLAlchemy."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Classe base para os modelos persistidos."""
