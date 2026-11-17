from datetime import datetime, timezone
import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.contracts import CompetitionFeatures, ProfileFeatures
from app.ai.dataset import TRAINING_DATA
from app.ai.model import classify, train_model
from app.ai.normalizer import FakeCompetitionNormalizer, OpenRouterCompetitionNormalizer
from app.db.runtime import get_session
from app.models.competition import Competition
from app.models.match import MatchEvaluation
from app.models.profile import Profile
from app.sources.contracts import ConcursoDetails

router = APIRouter(prefix="/recomendacoes", tags=["recomendacoes"])


@router.get("")
def get_recommendations(session: Session = Depends(get_session)) -> list[dict]:
    profile = session.get(Profile, 1)
    if profile is None:
        raise HTTPException(status_code=400, detail="Configure o perfil antes de buscar recomendações.")

    model = train_model(TRAINING_DATA)
    profile_features = ProfileFeatures(
        education=profile.education_level,
        areas=split_values(profile.knowledge_areas),
        skills=split_values(profile.knowledge_areas),
        experience=split_values(profile.experience),
        target_positions=split_values(profile.target_positions),
        states=profile.states,
        minimum_salary=profile.minimum_salary,
        description=profile.description,
    )
    fallback_normalizer = FakeCompetitionNormalizer()
    normalizer = (
        OpenRouterCompetitionNormalizer()
        if os.getenv("OPENROUTER_API_KEY") and os.getenv("OPENROUTER_MODEL")
        else fallback_normalizer
    )
    results = []
    for competition in session.scalars(select(Competition)).all():
        if profile.states and competition.state not in profile.states:
            continue
        if competition.details_processed_at is None:
            continue
        details = ConcursoDetails(
            source=competition.source,
            source_url=competition.source_url,
            title=competition.title or competition.organization,
            summary=competition.summary,
            author=competition.author,
            published_at=competition.published_at,
            updated_at=competition.source_updated_at,
            introduction=competition.introduction,
            sections=competition.sections,
            content=competition.content or "",
            links=competition.links,
        )
        try:
            normalized = normalizer.normalize(details)
        except Exception:
            if normalizer is fallback_normalizer:
                raise
            normalized = fallback_normalizer.normalize(details)
        normalized = normalized.model_copy(
            update={"state": competition.state, "organization": competition.organization}
        )
        prediction = classify(model, profile_features, normalized)
        compatibility_score, score_breakdown = calculate_compatibility_score(
            profile_features,
            normalized,
            prediction.probabilities,
        )
        classification_label = (
            prediction.classification
            if prediction.confidence >= 0.55
            else "incerta"
        )
        reasons, gaps = explain_match(profile_features, normalized)
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        match = session.scalar(
            select(MatchEvaluation).where(
                MatchEvaluation.profile_id == 1,
                MatchEvaluation.competition_id == competition.id,
            )
        )
        if match is None:
            match = MatchEvaluation(profile_id=1, competition_id=competition.id, created_at=now)
            session.add(match)
        match.classification = prediction.classification
        match.confidence = prediction.confidence
        match.probabilities = prediction.probabilities
        match.input_text = prediction.input_text
        match.updated_at = now
        results.append(
            {
                "id": competition.id,
                "source": competition.source,
                "title": competition.title or competition.organization,
                "organization": competition.organization,
                "state": competition.state,
                "source_status": competition.source_status,
                "classification": prediction.classification,
                "classification_label": classification_label,
                "compatibility_score": compatibility_score,
                "score_breakdown": score_breakdown,
                "confidence": prediction.confidence,
                "probabilities": prediction.probabilities,
                "reasons": reasons,
                "gaps": gaps,
                "education_required": normalized.education_required,
                "areas": normalized.areas,
                "positions": normalized.positions,
                "salary_identified": normalized.salary_min,
                "summary": competition.summary,
                "source_url": competition.source_url,
            }
        )
    session.commit()
    close = getattr(normalizer, "close", None)
    if close:
        close()
    return sorted(results, key=lambda item: item["compatibility_score"], reverse=True)


def split_values(value: str) -> list[str]:
    return [item.strip().lower() for item in value.replace(";", ",").split(",") if item.strip()]


def explain_match(profile: ProfileFeatures, competition: CompetitionFeatures) -> tuple[list[str], list[str]]:
    """Gera evidências legíveis sem substituir a decisão do modelo treinado."""
    reasons = ["Estado do concurso está entre os estados selecionados."]
    gaps = []
    profile_terms = set(profile.areas + profile.skills + profile.target_positions)
    competition_terms = set(competition.areas + competition.positions + competition.activities)
    overlap = sorted(profile_terms & competition_terms)
    if overlap:
        reasons.append(f"Termos em comum: {', '.join(overlap)}.")
    else:
        gaps.append("Nenhuma área, habilidade ou posição do perfil foi identificada no concurso.")
    if competition.education_required:
        if competition.education_required == profile.education:
            reasons.append("A escolaridade informada coincide com a exigida.")
        else:
            gaps.append(
                f"Escolaridade identificada: {competition.education_required}; perfil: {profile.education}."
            )
    else:
        gaps.append("A escolaridade exigida não foi identificada no texto.")
    if competition.salary_min is not None:
        if profile.minimum_salary is not None and competition.salary_min >= profile.minimum_salary:
            reasons.append(
                f"Salário identificado (R$ {competition.salary_min:,.2f}) atende ao mínimo informado."
            )
        else:
            reasons.append(f"Salário identificado no texto: R$ {competition.salary_min:,.2f}.")
            if profile.minimum_salary is not None:
                gaps.append("O salário identificado não atinge o mínimo informado.")
    else:
        gaps.append("Salário não foi identificado nos detalhes processados.")
    if not competition.positions:
        gaps.append("As posições não foram identificadas com segurança nos detalhes.")
    return reasons, gaps


def calculate_compatibility_score(
    profile: ProfileFeatures,
    competition: CompetitionFeatures,
    probabilities: dict[str, float],
) -> tuple[int, dict[str, int]]:
    """Calcula um índice explicável sem substituir o classificador treinado."""
    model_score = round(
        100 * (probabilities.get("alta", 0.0) + probabilities.get("media", 0.0) * 0.5)
    )
    profile_areas = {item.lower() for item in profile.areas}
    competition_areas = {item.lower() for item in competition.areas}
    profile_positions = {item.lower() for item in profile.target_positions}
    competition_positions = {item.lower() for item in competition.positions}
    area_points = 40 if profile_areas & competition_areas else 0
    position_points = 25 if profile_positions & competition_positions else 0
    education_points = 20 if competition.education_required == profile.education else 0
    salary_points = 0
    if profile.minimum_salary is not None and competition.salary_min is not None:
        salary_points = 15 if competition.salary_min >= profile.minimum_salary else 0
    evidence_score = area_points + position_points + education_points + salary_points
    score = round(model_score * 0.55 + evidence_score * 0.45)
    return min(100, max(0, score)), {
        "modelo": model_score,
        "areas": area_points,
        "posicoes": position_points,
        "escolaridade": education_points,
        "salario": salary_points,
    }
