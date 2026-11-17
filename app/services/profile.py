"""Serviço do perfil single-user."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.profile import Profile
from app.schemas.profile import ProfilePayload


def save_profile(session: Session, payload: ProfilePayload) -> Profile:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    profile = session.get(Profile, 1)
    if profile is None:
        profile = Profile(id=1, created_at=now, updated_at=now)
        session.add(profile)
    for field, value in payload.model_dump().items():
        setattr(profile, field, value)
    profile.updated_at = now
    session.commit()
    session.refresh(profile)
    return profile


def profile_payload(profile: Profile | None) -> dict:
    if profile is None:
        return {"configured": False}
    return {
        "configured": True,
        "id": profile.id,
        "name": profile.name,
        "education_level": profile.education_level,
        "education": profile.education,
        "target_positions": profile.target_positions,
        "knowledge_areas": profile.knowledge_areas,
        "experience": profile.experience,
        "minimum_salary": profile.minimum_salary,
        "states": profile.states,
        "description": profile.description,
    }
