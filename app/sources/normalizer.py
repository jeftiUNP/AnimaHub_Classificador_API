"""Conversão do contrato da fonte primária para o contrato do AnimaHub."""

from datetime import datetime
from typing import Any

from app.sources.contracts import ConcursoDetails, ConcursoLink, ConcursoListing, ConcursoSection
from app.sources.errors import ConcursoSourceError


def normalize_listing(payload: Any, state: str, source: str = "concursos_publicos_api") -> ConcursoListing:
    """Normaliza um item retornado por ``GET /concursos/{uf}``."""
    if not isinstance(payload, dict):
        raise ConcursoSourceError("O item da listagem não é um objeto JSON.")

    try:
        return ConcursoListing(
            source=source,
            state=state.upper(),
            source_url=payload["link"],
            organization=payload["organization"],
            source_status=payload["status"],
            vacancies_text=payload.get("workPlacesAvailable"),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ConcursoSourceError("A estrutura da listagem da fonte mudou.") from error


def normalize_details(payload: Any, source: str = "concursos_publicos_api") -> ConcursoDetails:
    """Normaliza o retorno de ``GET /concursos/detalhes``."""
    if not isinstance(payload, dict):
        raise ConcursoSourceError("Os detalhes não são um objeto JSON.")

    try:
        return ConcursoDetails(
            source=source,
            source_url=payload["link"],
            title=payload["title"],
            summary=payload.get("summary"),
            author=payload.get("author"),
            published_at=parse_datetime(payload.get("publishedAt")),
            updated_at=parse_datetime(payload.get("updatedAt")),
            introduction=payload.get("introduction") or [],
            sections=[ConcursoSection(**section) for section in payload.get("sections", [])],
            content=payload["content"],
            links=[ConcursoLink(**link) for link in payload.get("links", [])],
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ConcursoSourceError("A estrutura dos detalhes da fonte mudou.") from error


def parse_datetime(value: str | None) -> datetime | None:
    """Converte datas ISO da fonte sem impedir detalhes sem data."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ConcursoSourceError(f"Data inválida recebida da fonte: {value}") from error
