from pydantic import BaseModel, Field


class FounderJourneyCreate(BaseModel):

    journey_type: str = Field(
        ...,
        description=(
            "Current entrepreneurial journey. "
            "Allowed values: NO_IDEA, HAVE_IDEA, EXISTING_STARTUP"
        )
    )

    current_situation: str | None = Field(
        default=None,
        max_length=2000
    )

    goal: str | None = Field(
        default=None,
        max_length=2000
    )


class FounderJourneyUpdate(BaseModel):

    journey_type: str | None = Field(
        default=None,
        description=(
            "Current entrepreneurial journey. "
            "Allowed values: NO_IDEA, HAVE_IDEA, EXISTING_STARTUP"
        )
    )

    current_situation: str | None = Field(
        default=None,
        max_length=2000
    )

    goal: str | None = Field(
        default=None,
        max_length=2000
    )


class FounderJourneyResponse(BaseModel):

    id: int

    user_id: int

    journey_type: str

    current_situation: str | None

    goal: str | None

    model_config = {
        "from_attributes": True
    }