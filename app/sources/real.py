"""Adaptador da API existente de concursos públicos."""

from typing import Any

import httpx
from pydantic import HttpUrl

from app.sources.contracts import ConcursoDetails, ConcursoListing
from app.sources.errors import ConcursoSourceError
from app.sources.normalizer import normalize_details, normalize_listing


class ApiConcursoSource:
    """Consome a API Flask local em ``concursosPublicosAPI``."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:5000",
        client: httpx.Client | None = None,
        timeout: float = 20.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._client = client or httpx.Client(timeout=timeout)
        self._owns_client = client is None

    def __enter__(self) -> "ApiConcursoSource":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def list_concursos(self, state: str) -> list[ConcursoListing]:
        """Consulta uma UF e normaliza todos os itens retornados."""
        normalized_state = state.strip().lower()
        if len(normalized_state) != 2 or not normalized_state.isalpha():
            raise ConcursoSourceError("Informe uma UF com duas letras.")

        payload = self._get_json(f"/concursos/{normalized_state}")
        if not isinstance(payload, list):
            raise ConcursoSourceError("A listagem da fonte não é uma lista JSON.")
        return [normalize_listing(item, normalized_state) for item in payload]

    def get_details(self, url: str | HttpUrl) -> ConcursoDetails:
        """Consulta e normaliza os detalhes de uma publicação."""
        payload = self._get_json("/concursos/detalhes", params={"url": str(url)})
        return normalize_details(payload)

    def _get_json(self, path: str, params: dict[str, str] | None = None) -> Any:
        try:
            response = self._client.get(f"{self.base_url}{path}", params=params)
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError) as error:
            raise ConcursoSourceError("Não foi possível consultar a fonte de concursos.") from error
