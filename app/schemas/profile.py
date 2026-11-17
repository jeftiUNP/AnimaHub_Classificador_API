"""Schemas HTTP do perfil único."""

from pydantic import BaseModel, Field, field_validator


VALID_STATES = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG",
    "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
}


class ProfilePayload(BaseModel):
    name: str = Field(min_length=1)
    education_level: str = Field(min_length=1)
    education: str = Field(min_length=1)
    target_positions: str = ""
    knowledge_areas: str = ""
    experience: str = ""
    minimum_salary: float | None = None
    states: list[str] = Field(min_length=1)
    description: str = ""

    @field_validator("states")
    @classmethod
    def normalize_states(cls, states: list[str]) -> list[str]:
        normalized = list(dict.fromkeys(state.strip().upper() for state in states if state.strip()))
        invalid = sorted(set(normalized) - VALID_STATES)
        if not normalized or invalid:
            raise ValueError(f"Estados inválidos: {', '.join(invalid) or 'nenhum estado informado'}")
        return normalized
