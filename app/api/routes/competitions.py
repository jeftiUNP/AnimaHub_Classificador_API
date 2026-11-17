from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.runtime import get_session
from app.models.profile import Profile
from app.services.sync import list_competitions

router = APIRouter(prefix="/concursos", tags=["concursos"])


@router.get("")
def get_competitions(session: Session = Depends(get_session)) -> list[dict]:
    profile = session.get(Profile, 1)
    allowed_states = set(profile.states) if profile and profile.states else None
    return [
        {
            "id": competition.id,
            "source": competition.source,
            "title": competition.title or competition.organization,
            "organization": competition.organization,
            "state": competition.state,
            "status": competition.source_status,
            "published_at": competition.published_at,
            "source_url": competition.source_url,
            "summary": competition.summary,
            "vacancies": competition.vacancies_text,
        }
        for competition in list_competitions(session)
        if (not allowed_states or competition.state in allowed_states)
        and competition.details_processed_at is not None
    ]
