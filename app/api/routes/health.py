"""Endpoint de verificação de disponibilidade da API."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Retorna o estado atual da API."""
    return {"status": "ok"}
