from pydantic import BaseModel, Field


class StartupIdeaRequest(BaseModel):
    idea: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Startup idea that needs to be analyzed"
    )


class StartupIdeaAnalysisResponse(BaseModel):
    problem: str
    target_customers: str
    market_opportunity: str
    competitors: list[str]
    unique_value_proposition: str
    business_model: str
    risks: list[str]
    mvp_features: list[str]
    recommendations: list[str]


class StartupScoreResponse(BaseModel):
    problem_severity: int = Field(
        ...,
        ge=1,
        le=10,
        description="How serious and important the problem is"
    )

    market_opportunity: int = Field(
        ...,
        ge=1,
        le=10,
        description="Potential size and attractiveness of the market"
    )

    competition: int = Field(
        ...,
        ge=1,
        le=10,
        description="Competitive attractiveness; higher means better opportunity"
    )

    business_model: int = Field(
        ...,
        ge=1,
        le=10,
        description="Strength and viability of the business model"
    )

    mvp_feasibility: int = Field(
        ...,
        ge=1,
        le=10,
        description="How realistically the MVP can be built"
    )

    scalability: int = Field(
        ...,
        ge=1,
        le=10,
        description="Potential to scale the startup"
    )

    overall_score: float = Field(
        ...,
        ge=1,
        le=10,
        description="Overall startup score"
    )

    strengths: list[str]

    weaknesses: list[str]

    validation_experiments: list[str]

    final_recommendation: str