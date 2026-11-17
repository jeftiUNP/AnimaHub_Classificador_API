"""Contratos de entrada e saída do classificador de compatibilidade."""

from pydantic import BaseModel, Field


class ProfileFeatures(BaseModel):
    """Perfil reduzido usado pelo modelo treinado."""

    education: str
    areas: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    target_positions: list[str] = Field(default_factory=list)
    states: list[str] = Field(default_factory=list)
    minimum_salary: float | None = None
    description: str = ""


class CompetitionFeatures(BaseModel):
    """Dados normalizados de um concurso antes da classificação."""

    title: str
    organization: str = ""
    state: str
    education_required: str | None = None
    areas: list[str] = Field(default_factory=list)
    activities: list[str] = Field(default_factory=list)
    requirements: list[str] = Field(default_factory=list)
    positions: list[str] = Field(default_factory=list)
    salary_min: float | None = None
    content: str = ""


class PredictionResult(BaseModel):
    """Resultado produzido pelo classificador treinado."""

    classification: str
    confidence: float = Field(ge=0, le=1)
    probabilities: dict[str, float]
    input_text: str


class NormalizedCompetition(BaseModel):
    """Resposta esperada do normalizador via OpenRouter."""

    education_required: str | None = None
    areas: list[str] = Field(default_factory=list)
    activities: list[str] = Field(default_factory=list)
    requirements: list[str] = Field(default_factory=list)
    positions: list[str] = Field(default_factory=list)
    salary_min: float | None = None
    salary_max: float | None = None
    registration_end: str | None = None
    evidence: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0, le=1)
