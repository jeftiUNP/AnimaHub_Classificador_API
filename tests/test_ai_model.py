import json
from pathlib import Path

import httpx

from app.ai.contracts import CompetitionFeatures, ProfileFeatures
from app.ai.dataset import TRAINING_DATA
from app.ai.model import classify, train_model
from app.ai.normalizer import FakeCompetitionNormalizer, OpenRouterCompetitionNormalizer
from app.sources.fake import FakeConcursoSource


FIXTURE = Path(__file__).parents[1] / "app" / "sources" / "fixtures" / "concursos_fake.json"


def test_trained_model_classifies_compatible_and_incompatible_examples() -> None:
    model = train_model(TRAINING_DATA)
    compatible = classify(
        model,
        ProfileFeatures(education="superior", areas=["tecnologia"], skills=["programacao"], states=["CE"]),
        CompetitionFeatures(title="Analista TI", state="CE", education_required="superior", areas=["tecnologia"], activities=["programacao"]),
    )
    incompatible = classify(
        model,
        ProfileFeatures(education="superior", areas=["direito"], skills=["legislacao"], states=["CE"]),
        CompetitionFeatures(title="Analista TI", state="CE", education_required="superior", areas=["tecnologia"], activities=["programacao"]),
    )

    assert compatible.classification == "alta"
    assert incompatible.classification == "baixa"
    assert 0 <= compatible.confidence <= 1
    assert set(compatible.probabilities) == {"alta", "baixa", "media"}


def test_fake_normalizer_works_without_external_llm() -> None:
    source = FakeConcursoSource(FIXTURE)
    listing = source.list_concursos("CE")[0]
    details = source.get_details(listing.source_url)

    normalized = FakeCompetitionNormalizer().normalize(details)

    assert normalized.title == details.title
    assert "tecnologia" in normalized.areas
    assert normalized.education_required == "superior"


def test_openrouter_normalizer_uses_chat_completions_contract() -> None:
    source = FakeConcursoSource(FIXTURE)
    listing = source.list_concursos("CE")[0]
    details = source.get_details(listing.source_url)
    requests_seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests_seen.append(request)
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "education_required": "superior",
                                    "areas": ["tecnologia"],
                                    "activities": ["analise de sistemas"],
                                    "requirements": ["curso superior"],
                                    "positions": ["analista"],
                                    "salary_min": 7000,
                                    "salary_max": None,
                                    "registration_end": None,
                                    "evidence": ["curso superior"],
                                    "confidence": 0.9,
                                }
                            )
                        }
                    }
                ]
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    normalizer = OpenRouterCompetitionNormalizer(
        api_key="test-key",
        model="test-model",
        base_url="https://openrouter.test/api/v1",
        client=client,
    )

    normalized = normalizer.normalize(details)

    assert normalized.areas == ["tecnologia"]
    assert normalized.salary_min == 7000
    assert requests_seen[0].url.path == "/api/v1/chat/completions"
    assert requests_seen[0].headers["authorization"] == "Bearer test-key"
    client.close()
