from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.runtime import get_session
from app.models.profile import Profile
from app.services.sync import sync_competitions

router = APIRouter(prefix="/sincronizacao", tags=["sincronizacao"])


@router.post("")
def run_sync(
    fonte: str = Query("both", pattern="^(fake|real|both)$"),
    session: Session = Depends(get_session),
) -> dict:
    profile = session.get(Profile, 1)
    if profile is None or not profile.states:
        raise HTTPException(status_code=400, detail="Configure o perfil com pelo menos um estado.")
    result = sync_competitions(session, fonte, profile.states)
    return result.__dict__
