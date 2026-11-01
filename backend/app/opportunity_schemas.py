from pydantic import BaseModel


class OpportunityScoreBreakdown(BaseModel):
    total_score: int
    skills: int
    industry: int
    budget: int
    experience: int
    time: int
    business_preference: int
    risk: int
    goals: int


class OpportunityResponse(BaseModel):
    id: int
    founder_id: int
    title: str
    description: str
    industry: str | None
    required_skills: str | None
    required_experience: str | None
    target_customers: str | None
    business_model: str | None
    estimated_investment: int | None
    difficulty: str | None
    market_potential: int | None
    founder_fit_score: int | None
    why_it_fits: str | None
    risks: str | None
    recommended_next_step: str | None

    score_breakdown: OpportunityScoreBreakdown | None = None

    model_config = {"from_attributes": True}


class OpportunityGenerateResponse(BaseModel):
    message: str
    opportunities: list[OpportunityResponse]