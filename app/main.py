"""Ponto de entrada da API FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.competitions import router as competitions_router
from app.api.routes.health import router as health_router
from app.api.routes.profile import router as profile_router
from app.api.routes.recommendations import router as recommendations_router
from app.api.routes.sync import router as sync_router


def create_app() -> FastAPI:
    """Cria e configura a aplicação FastAPI."""
    application = FastAPI(
        title="AnimaHub Classificador API",
        description="API para o classificador e recomendador de concursos públicos.",
        version="0.1.0",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(health_router)
    application.include_router(profile_router)
    application.include_router(sync_router)
    application.include_router(competitions_router)
    application.include_router(recommendations_router)
    return application


app = create_app()
