from datetime import datetime

from pydantic import BaseModel


class WorkspaceStartup(BaseModel):
    id: int
    name: str
    description: str
    industry: str | None
    stage: str | None
    target_market: str | None
    business_model: str | None


class WorkspaceJourney(BaseModel):
    journey_type: str
    current_situation: str | None
    goal: str | None


class WorkspaceValidation(BaseModel):
    total_experiments: int
    planned: int
    in_progress: int
    completed: int
    cancelled: int
    completed_with_learning: int
    latest_decision: str | None
    confidence_score: int | None


class WorkspaceMVP(BaseModel):
    plan_id: int | None
    title: str | None
    status: str | None
    total_milestones: int
    completed_milestones: int
    total_tasks: int
    completed_tasks: int
    progress_percentage: float


class WorkspaceGrowth(BaseModel):
    assessment_id: int | None
    growth_score: int | None
    primary_bottleneck: str | None
    status: str | None
    has_assessment: bool
    recommendations: str | None
    action_plan: str | None
    assessed_at: datetime | None


class WorkspaceResponse(BaseModel):
    startup: WorkspaceStartup
    journey: WorkspaceJourney | None
    validation: WorkspaceValidation
    mvp: WorkspaceMVP
    growth: WorkspaceGrowth
    workspace_status: str
    next_recommended_action: str
    generated_at: datetime