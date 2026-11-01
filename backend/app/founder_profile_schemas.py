from pydantic import BaseModel, Field


class FounderProfileCreate(BaseModel):

    location: str | None = Field(
        default=None,
        max_length=150
    )

    education: str | None = Field(
        default=None,
        max_length=200
    )

    skills: str | None = None

    experience: str | None = None

    available_time: str | None = Field(
        default=None,
        max_length=100
    )

    budget: int | None = Field(
        default=None,
        ge=0
    )

    team_status: str | None = Field(
        default=None,
        max_length=100
    )

    interests: str | None = None

    preferred_industries: str | None = None

    business_preference: str | None = Field(
        default=None,
        max_length=100
    )

    risk_tolerance: str | None = Field(
        default=None,
        max_length=50
    )

    target_income: int | None = Field(
        default=None,
        ge=0
    )

    short_term_goal: str | None = None

    long_term_goal: str | None = None


class FounderProfileResponse(FounderProfileCreate):

    id: int
    user_id: int

    model_config = {
        "from_attributes": True
    }


class FounderProfileUpdate(BaseModel):

    location: str | None = Field(
        default=None,
        max_length=150
    )

    education: str | None = Field(
        default=None,
        max_length=200
    )

    skills: str | None = None

    experience: str | None = None

    available_time: str | None = Field(
        default=None,
        max_length=100
    )

    budget: int | None = Field(
        default=None,
        ge=0
    )

    team_status: str | None = Field(
        default=None,
        max_length=100
    )

    interests: str | None = None

    preferred_industries: str | None = None

    business_preference: str | None = Field(
        default=None,
        max_length=100
    )

    risk_tolerance: str | None = Field(
        default=None,
        max_length=50
    )

    target_income: int | None = Field(
        default=None,
        ge=0
    )

    short_term_goal: str | None = None

    long_term_goal: str | None = None