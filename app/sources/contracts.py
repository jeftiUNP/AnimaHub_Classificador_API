"""Contratos normalizados usados por todas as fontes de concursos."""

from datetime import datetime
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ConcursoListing(BaseModel):
    """Concurso encontrado na listagem de um estado."""

    model_config = ConfigDict(extra="forbid")

    source: str
    state: str = Field(min_length=2, max_length=2)
    source_url: HttpUrl
    organization: str
    source_status: str
    vacancies_text: str | None = None


class ConcursoSection(BaseModel):
    """Seção extraída do conteúdo de uma publicação."""

    title: str
    paragraphs: list[str] = Field(default_factory=list)


class ConcursoLink(BaseModel):
    """Link encontrado dentro do conteúdo da publicação."""

    text: str
    url: HttpUrl


class ConcursoDetails(BaseModel):
    """Detalhes normalizados de uma publicação de concurso."""

    model_config = ConfigDict(extra="forbid")

    source: str
    source_url: HttpUrl
    title: str
    summary: str | None = None
    author: str | None = None
    published_at: datetime | None = None
    updated_at: datetime | None = None
    introduction: list[str] = Field(default_factory=list)
    sections: list[ConcursoSection] = Field(default_factory=list)
    content: str
    links: list[ConcursoLink] = Field(default_factory=list)


class ConcursoSource(Protocol):
    """Interface mínima para uma fonte real ou fake."""

    def list_concursos(self, state: str) -> list[ConcursoListing]:
        """Retorna a listagem de uma UF."""

    def get_details(self, url: str | HttpUrl) -> ConcursoDetails:
        """Retorna os detalhes de uma publicação."""
