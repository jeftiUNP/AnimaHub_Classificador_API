"""Treinamento e predição do modelo de compatibilidade."""

from collections.abc import Iterable
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from app.ai.contracts import CompetitionFeatures, PredictionResult, ProfileFeatures


TrainingExample = tuple[str, str]


def build_model() -> Pipeline:
    """Cria o pipeline de ML usado pelo MVP."""
    return Pipeline(
        [
            ("tfidf", TfidfVectorizer(lowercase=True, ngram_range=(1, 2))),
            ("classifier", LogisticRegression(max_iter=1000, random_state=42)),
        ]
    )


def train_model(examples: Iterable[TrainingExample]) -> Pipeline:
    """Treina o classificador com textos e rótulos fornecidos."""
    rows = list(examples)
    if not rows:
        raise ValueError("É necessário fornecer exemplos de treinamento.")

    texts, labels = zip(*rows)
    model = build_model()
    model.fit(texts, labels)
    return model


def classify(
    model: Pipeline,
    profile: ProfileFeatures,
    competition: CompetitionFeatures,
) -> PredictionResult:
    """Classifica um perfil e concurso já normalizados."""
    input_text = build_input_text(profile, competition)
    probabilities = model.predict_proba([input_text])[0]
    classes = model.classes_.tolist()
    probability_map = {
        label: round(float(probability), 4)
        for label, probability in zip(classes, probabilities)
    }
    classification = str(model.predict([input_text])[0])
    return PredictionResult(
        classification=classification,
        confidence=round(max(probability_map.values()), 4),
        probabilities=probability_map,
        input_text=input_text,
    )


def build_input_text(profile: ProfileFeatures, competition: CompetitionFeatures) -> str:
    """Transforma os dois objetos em texto para o TF-IDF."""
    tokens = [
            f"formacao {profile.education}",
            f"areas perfil {' '.join(profile.areas)}",
            f"habilidades {' '.join(profile.skills)}",
            f"experiencia {' '.join(profile.experience)}",
            f"cargos desejados {' '.join(profile.target_positions)}",
            f"estados perfil {' '.join(profile.states)}",
            f"salario minimo {profile.minimum_salary or 0}",
            f"descricao perfil {profile.description}",
            f"concurso {competition.title}",
            f"orgao {competition.organization}",
            f"estado concurso {competition.state}",
            f"escolaridade exigida {competition.education_required or ''}",
            f"areas concurso {' '.join(competition.areas)}",
            f"atividades {' '.join(competition.activities)}",
            f"requisitos {' '.join(competition.requirements)}",
            f"cargos {' '.join(competition.positions)}",
            f"salario concurso {competition.salary_min or 0}",
            f"conteudo {competition.content}",
    ]
    tokens.extend(
        f"area_perfil_{slug(profile_area)}_area_concurso_{slug(competition_area)}"
        for profile_area in profile.areas
        for competition_area in competition.areas
    )
    tokens.extend(
        f"habilidade_perfil_{slug(skill)}_atividade_concurso_{slug(activity)}"
        for skill in profile.skills
        for activity in competition.activities
    )
    tokens.append(
        "estado_compativel"
        if competition.state.upper() in {state.upper() for state in profile.states}
        else "estado_incompativel"
    )
    tokens.append(
        "escolaridade_compativel"
        if profile.education == competition.education_required
        else "escolaridade_diferente"
    )
    if profile.minimum_salary is not None and competition.salary_min is not None:
        tokens.append(
            "salario_compativel"
            if competition.salary_min >= profile.minimum_salary
            else "salario_incompativel"
        )
    return " ".join(tokens)


def slug(value: str) -> str:
    """Converte um conceito em token estável para o vetor TF-IDF."""
    return re.sub(r"[^a-z0-9_]+", "_", value.lower()).strip("_")
