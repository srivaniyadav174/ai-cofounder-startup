from datetime import datetime

from pydantic import BaseModel, Field


# ============================================================
# VALIDATION EXPERIMENT
# ============================================================

class ValidationExperimentCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=250
    )

    hypothesis: str = Field(
        ...,
        min_length=10,
        max_length=3000
    )

    experiment_type: str = Field(
        ...,
        min_length=3,
        max_length=100
    )

    description: str = Field(
        ...,
        min_length=10,
        max_length=5000
    )

    success_criteria: str = Field(
        ...,
        min_length=5,
        max_length=3000
    )

    priority: int = Field(
        default=1,
        ge=1,
        le=5
    )


class ValidationExperimentUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=250
    )

    hypothesis: str | None = Field(
        default=None,
        min_length=10,
        max_length=3000
    )

    experiment_type: str | None = Field(
        default=None,
        min_length=3,
        max_length=100
    )

    description: str | None = Field(
        default=None,
        min_length=10,
        max_length=5000
    )

    success_criteria: str | None = Field(
        default=None,
        min_length=5,
        max_length=3000
    )

    status: str | None = Field(
        default=None,
        description=(
            "PLANNED, IN_PROGRESS, COMPLETED, "
            "or CANCELLED"
        )
    )

    result: str | None = Field(
        default=None,
        max_length=5000
    )

    learning: str | None = Field(
        default=None,
        max_length=5000
    )

    next_action: str | None = Field(
        default=None,
        max_length=5000
    )

    priority: int | None = Field(
        default=None,
        ge=1,
        le=5
    )


class ValidationExperimentResponse(BaseModel):
    id: int
    founder_id: int
    startup_id: int
    title: str
    hypothesis: str
    experiment_type: str
    description: str
    success_criteria: str
    status: str
    result: str | None
    learning: str | None
    next_action: str | None
    priority: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


# ============================================================
# VALIDATION SUMMARY
# ============================================================

class ValidationSummaryResponse(BaseModel):
    startup_id: int
    total_experiments: int
    planned: int
    in_progress: int
    completed: int
    cancelled: int
    completed_with_learning: int
    recommendation: str


# ============================================================
# VALIDATION DECISION
# ============================================================

class ValidationDecisionResponse(BaseModel):
    id: int
    founder_id: int
    startup_id: int

    decision: str = Field(
        description=(
            "PROCEED_TO_MVP, CONTINUE_VALIDATION, "
            "PIVOT, or STOP"
        )
    )

    confidence_score: int = Field(
        ge=1,
        le=100
    )

    evidence_summary: str

    strengths: str | None

    weaknesses: str | None

    key_learnings: str | None

    recommendation: str

    mvp_scope: str | None

    next_actions: str | None

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }