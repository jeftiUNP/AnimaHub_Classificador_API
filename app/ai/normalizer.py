"""Normalização fake e integração opcional com o OpenRouter."""

import json
import os
import re
from typing import Any

import httpx

from app.ai.contracts import CompetitionFeatures, NormalizedCompetition
from app.sources.contracts import ConcursoDetails


class FakeCompetitionNormalizer:
    """Normaliza concursos sem internet para testes e apresentação."""

    def normalize(self, details: ConcursoDetails) -> CompetitionFeatures:
        text = " ".join(
            [
                details.title,
                details.summary or "",
                *details.introduction,
                *(paragraph for section in details.sections for paragraph in section.paragraphs),
            ]
        ).lower()
        areas = []
        if any(word in text for word in ("tecnologia", "sistema", "programação", "software")):
            areas.append("tecnologia")
        if any(word in text for word in ("processo", "gestão", "administrativ")):
            areas.append("gestao")
        if any(word in text for word in ("educação", "pedagog", "professor")):
            areas.append("educacao")
        if any(word in text for word in ("direito", "jurídic", "legisla", "procurador")):
            areas.append("direito")
        if any(word in text for word in ("saúde", "médic", "enferm", "hospital")):
            areas.append("saude")
        if any(word in text for word in ("engenheir", "obras", "projetos")):
            areas.append("engenharia")
        if any(word in text for word in ("auditor", "contábil", "contabilidade", "finanças")):
            areas.append("contabilidade")
        education = "superior" if any(word in text for word in ("superior", "graduação")) else None
        salary_match = re.search(r"(?:r\$|salário(?:s)?(?: de| até)?)\s*([\d.]+(?:,\d+)?)\s*(mil)?", text)
        salary = None
        if salary_match:
            salary = float(salary_match.group(1).replace(".", "").replace(",", "."))
            if salary_match.group(2):
                salary *= 1000
        positions = sorted(
            {
                word
                for word in (
                    "analista", "desenvolvedor", "técnico", "professor", "médico",
                    "enfermeiro", "auditor", "engenheiro", "agente", "delegado",
                    "escrivão", "policial", "guarda", "recenseador", "assistente",
                )
                if word in text
            }
        )
        return CompetitionFeatures(
            title=details.title,
            state="??",
            education_required=education,
            areas=areas,
            activities=[section.title for section in details.sections],
            requirements=[paragraph for section in details.sections for paragraph in section.paragraphs],
            positions=positions,
            content=details.content,
            salary_min=salary,
        )


class OpenRouterCompetitionNormalizer:
    """Usa o OpenRouter para transformar texto irregular em JSON."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model or os.getenv("OPENROUTER_MODEL")
        self.base_url = (base_url or os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")).rstrip("/")
        self._client = client or httpx.Client(timeout=45)
        self._owns_client = client is None

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def normalize(self, details: ConcursoDetails) -> CompetitionFeatures:
        if not self.api_key or not self.model:
            raise RuntimeError("Configure OPENROUTER_API_KEY e OPENROUTER_MODEL.")
        prompt = self._build_prompt(details)
        response = self._client.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={
                "model": self.model,
                "temperature": 0,
                "messages": [
                    {"role": "system", "content": "Retorne somente JSON válido, sem markdown."},
                    {"role": "user", "content": prompt},
                ],
            },
        )
        response.raise_for_status()
        payload = response.json()
        content = payload["choices"][0]["message"]["content"]
        normalized = NormalizedCompetition.model_validate(json.loads(content))
        return CompetitionFeatures(
            title=details.title,
            state="??",
            education_required=normalized.education_required,
            areas=normalized.areas,
            activities=normalized.activities,
            requirements=normalized.requirements,
            positions=normalized.positions,
            salary_min=normalized.salary_min,
            content=details.content,
        )

    @staticmethod
    def _build_prompt(details: ConcursoDetails) -> str:
        return f"""Normalize o concurso abaixo para análise de compatibilidade.
Não invente informações. Use null ou listas vazias quando o dado não existir.
Retorne exatamente este JSON: {{\"education_required\": null, \"areas\": [], \"activities\": [], \"requirements\": [], \"positions\": [], \"salary_min\": null, \"salary_max\": null, \"registration_end\": null, \"evidence\": [], \"confidence\": 0}}

Título: {details.title}
Resumo: {details.summary or ''}
Conteúdo: {details.content}
Seções: {details.sections}
"""
