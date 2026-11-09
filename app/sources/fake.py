"""Fonte local para demonstrações e testes offline."""

import json
from pathlib import Path
from typing import Any

from pydantic import HttpUrl

from app.sources.contracts import ConcursoDetails, ConcursoListing
from app.sources.normalizer import normalize_details, normalize_listing


DEFAULT_FIXTURE = Path(__file__).parent / "fixtures" / "concursos_fake.json"


class FakeConcursoSource:
    """Implementa o mesmo contrato da fonte real usando um JSON local."""

    def __init__(self, fixture_path: str | Path = DEFAULT_FIXTURE) -> None:
        self.fixture_path = Path(fixture_path)
        self.payload = self._load_fixture()

    def list_concursos(self, state: str) -> list[ConcursoListing]:
        normalized_state = state.strip().lower()
        items = self.payload.get("listings", {}).get(normalized_state, [])
        return [normalize_listing(item, normalized_state, source="fake") for item in items]

    def get_details(self, url: str | HttpUrl) -> ConcursoDetails:
        payload = self.payload.get("details", {}).get(str(url))
        if payload is None:
            raise KeyError(f"Detalhes fake não encontrados para {url}.")
        return normalize_details(payload, source="fake")

    def _load_fixture(self) -> dict[str, Any]:
        with self.fixture_path.open(encoding="utf-8") as fixture:
            payload = json.load(fixture)
        if not isinstance(payload, dict):
            raise ValueError("O fixture fake deve conter um objeto JSON.")
        return payload
