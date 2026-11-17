from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.runtime import get_session
from app.models.profile import Profile
from app.schemas.profile import ProfilePayload
from app.services.profile import profile_payload, save_profile

router = APIRouter(prefix="/perfil", tags=["perfil"])


@router.get("")
def get_profile(session: Session = Depends(get_session)) -> dict:
    return profile_payload(session.get(Profile, 1))


@router.put("")
def put_profile(payload: ProfilePayload, session: Session = Depends(get_session)) -> dict:
    return profile_payload(save_profile(session, payload))
