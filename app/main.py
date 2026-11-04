"""Ponto de entrada da API FastAPI."""

from fastapi import FastAPI

from app.api.routes.health import router as health_router


def create_app() -> FastAPI:
    """Cria e configura a aplicação FastAPI."""
    application = FastAPI(
        title="AnimaHub Classificador API",
        description="API para o classificador e recomendador de concursos públicos.",
        version="0.1.0",
    )
    application.include_router(health_router)
    return application


app = create_app()
