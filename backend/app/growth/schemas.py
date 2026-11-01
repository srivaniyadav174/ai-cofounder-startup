from datetime import datetime

from pydantic import BaseModel, Field


class GrowthAssessmentCreate(BaseModel):

    monthly_revenue: int | None = Field(
        default=None,
        ge=0
    )

    monthly_customers: int | None = Field(
        default=None,
        ge=0
    )

    monthly_growth_percentage: int | None = Field(
        default=None,
        ge=-100,
        le=1000
    )

    conversion_rate_percentage: int | None = Field(
        default=None,
        ge=0,
        le=100
    )

    retention_rate_percentage: int | None = Field(
        default=None,
        ge=0,
        le=100
    )

    churn_rate_percentage: int | None = Field(
        default=None,
        ge=0,
        le=100
    )

    average_revenue_per_customer: int | None = Field(
        default=None,
        ge=0
    )

    acquisition_channels: str | None = Field(
        default=None,
        max_length=5000
    )

    pricing_model: str | None = Field(
        default=None,
        max_length=150
    )

    sales_process: str | None = Field(
        default=None,
        max_length=5000
    )

    competitive_landscape: str | None = Field(
        default=None,
        max_length=5000
    )

    current_challenges: str | None = Field(
        default=None,
        max_length=5000
    )

    growth_goal: str | None = Field(
        default=None,
        max_length=5000
    )


class GrowthAssessmentResponse(BaseModel):

    id: int
    founder_id: int
    startup_id: int

    monthly_revenue: int | None
    monthly_customers: int | None
    monthly_growth_percentage: int | None
    conversion_rate_percentage: int | None
    retention_rate_percentage: int | None
    churn_rate_percentage: int | None
    average_revenue_per_customer: int | None

    acquisition_channels: str | None
    pricing_model: str | None
    sales_process: str | None
    competitive_landscape: str | None
    current_challenges: str | None
    growth_goal: str | None

    growth_score: int | None
    primary_bottleneck: str | None
    root_causes: str | None
    growth_opportunities: str | None
    recommendations: str | None
    action_plan: str | None

    status: str

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class GrowthSummaryResponse(BaseModel):

    startup_id: int

    growth_score: int | None
    primary_bottleneck: str | None

    assessment_status: str

    recommendations: str | None
    action_plan: str | None

    created_at: datetime | None
    updated_at: datetime | None