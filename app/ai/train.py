"""Comandos de treinamento e avaliação do classificador."""

from pathlib import Path

import joblib
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

from app.ai.dataset import TRAINING_DATA
from app.ai.model import build_model, train_model


def evaluate_training_data() -> tuple[object, str]:
    """Avalia uma divisão dos dados sintéticos e treina o modelo final."""
    texts, labels = zip(*TRAINING_DATA)
    train_texts, test_texts, train_labels, test_labels = train_test_split(
        texts,
        labels,
        test_size=0.3,
        random_state=42,
        stratify=labels,
    )
    evaluation_model = build_model()
    evaluation_model.fit(train_texts, train_labels)
    report = classification_report(test_labels, evaluation_model.predict(test_texts), zero_division=0)
    return train_model(TRAINING_DATA), report


def train_and_save(output_path: str | Path = "artifacts/compatibility_model.joblib") -> str:
    """Treina o modelo final, salva o artefato e retorna o relatório."""
    model, report = evaluate_training_data()
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
    return report


if __name__ == "__main__":
    print(train_and_save())
