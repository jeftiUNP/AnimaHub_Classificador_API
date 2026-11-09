import json
from pathlib import Path

import httpx
import pytest

from app.sources.errors import ConcursoSourceError
from app.sources.fake import FakeConcursoSource
from app.sources.real import ApiConcursoSource


FIXTURE = Path(__file__).parents[1] / "app" / "sources" / "fixtures" / "concursos_fake.json"


def test_fake_source_uses_the_normalized_contract() -> None:
    source = FakeConcursoSource(FIXTURE)

    listings = source.list_concursos("CE")
    details = source.get_details(listings[0].source_url)

    assert len(listings) == 2
    assert listings[0].source == "fake"
    assert listings[0].state == "CE"
    assert listings[0].source_status == "open"
    assert details.title == "Concurso para Analista de Tecnologia"
    assert details.published_at is not None
    assert details.sections[0].title == "Requisitos"


def test_real_source_adapts_listing_and_details_routes() -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    requests_seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests_seen.append(request)
        if request.url.path == "/concursos/ce":
            return httpx.Response(200, json=fixture["listings"]["ce"])
        if request.url.path == "/concursos/detalhes":
            return httpx.Response(200, json=fixture["details"][fixture["listings"]["ce"][0]["link"]])
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    source = ApiConcursoSource(base_url="http://source.test", client=client)

    listings = source.list_concursos("CE")
    details = source.get_details(listings[0].source_url)

    assert len(listings) == 2
    assert listings[1].organization == "Instituto Público do Ceará"
    assert details.source == "concursos_publicos_api"
    assert details.content.startswith("O concurso oferece")
    assert requests_seen[0].url.path == "/concursos/ce"
    assert requests_seen[1].url.path == "/concursos/detalhes"
    assert requests_seen[1].url.params["url"] == str(listings[0].source_url)
    client.close()


def test_real_source_rejects_invalid_state() -> None:
    source = ApiConcursoSource(client=httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(200))))

    with pytest.raises(ConcursoSourceError, match="duas letras"):
        source.list_concursos("Ceará")

    source._client.close()
