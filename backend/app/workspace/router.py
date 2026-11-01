from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db

from app.models.user import User
from app.models.startup import Startup
from app.models.founder_journey import FounderJourney
from app.models.validation_experiment import ValidationExperiment
from app.models.validation_decision import ValidationDecision
from app.models.mvp_plan import MVPPlan
from app.models.mvp_milestone import MVPMilestone
from app.models.mvp_task import MVPTask
from app.models.growth_assessment import GrowthAssessment

from app.workspace.schemas import (
WorkspaceResponse,
WorkspaceStartup,
WorkspaceJourney,
WorkspaceValidation,
WorkspaceMVP,
WorkspaceGrowth,
)

router = APIRouter(
prefix="/workspace",
tags=["Startup Workspace"],
)

def get_owned_startup(
    startup_id: int,
    current_user: User,
    db: Session,
    ) -> Startup:
    startup = (
    db.query(Startup)
    .filter(
    Startup.id == startup_id,
    Startup.founder_id == current_user.id,
    )
    .first()
    )

    if not startup:
        raise HTTPException(
            status_code=404,
            detail="Startup not found",
        )

    return startup

@router.get(
"/{startup_id}",
response_model=WorkspaceResponse,
)
def get_startup_workspace(
    startup_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ):
    startup = get_owned_startup(
    startup_id,
    current_user,
    db,
    )

    journey = (
        db.query(FounderJourney)
        .filter(
            FounderJourney.user_id == current_user.id,
        )
        .order_by(FounderJourney.id.desc())
        .first()
    )

    experiments = (
        db.query(ValidationExperiment)
        .filter(
            ValidationExperiment.startup_id == startup.id,
            ValidationExperiment.founder_id == current_user.id,
        )
        .order_by(ValidationExperiment.id.desc())
        .all()
    )

    validation_decision = (
        db.query(ValidationDecision)
        .filter(
            ValidationDecision.startup_id == startup.id,
            ValidationDecision.founder_id == current_user.id,
        )
        .order_by(ValidationDecision.id.desc())
        .first()
    )

    mvp_plan = (
        db.query(MVPPlan)
        .filter(
            MVPPlan.startup_id == startup.id,
            MVPPlan.founder_id == current_user.id,
        )
        .order_by(MVPPlan.id.desc())
        .first()
    )

    milestones = []
    tasks = []

    if mvp_plan:
        milestones = (
            db.query(MVPMilestone)
            .filter(
                MVPMilestone.startup_id == startup.id,
                MVPMilestone.founder_id == current_user.id,
                MVPMilestone.mvp_plan_id == mvp_plan.id,
            )
            .order_by(MVPMilestone.order_index.asc())
            .all()
        )

        tasks = (
            db.query(MVPTask)
            .filter(
                MVPTask.startup_id == startup.id,
                MVPTask.founder_id == current_user.id,
                MVPTask.mvp_plan_id == mvp_plan.id,
            )
            .order_by(MVPTask.id.asc())
            .all()
        )

    growth_assessment = (
        db.query(GrowthAssessment)
        .filter(
            GrowthAssessment.startup_id == startup.id,
            GrowthAssessment.founder_id == current_user.id,
        )
        .order_by(GrowthAssessment.id.desc())
        .first()
    )

    completed_experiments = sum(
        1
        for experiment in experiments
        if experiment.status == "COMPLETED"
    )

    completed_tasks = sum(
        1
        for task in tasks
        if task.status == "COMPLETED"
    )

    completed_milestones = sum(
        1
        for milestone in milestones
        if milestone.status == "COMPLETED"
    )

    startup_response = WorkspaceStartup.model_validate(
        startup,
        from_attributes=True,
    )

    journey_response = None

    if journey:
        journey_response = WorkspaceJourney.model_validate(
            journey,
            from_attributes=True,
        )

    validation_response = WorkspaceValidation(
        experiments=experiments,
        decision=validation_decision,
        completed_experiments=completed_experiments,
        total_experiments=len(experiments),
    )

    mvp_response = WorkspaceMVP(
        plan=mvp_plan,
        milestones=milestones,
        tasks=tasks,
        completed_milestones=completed_milestones,
        total_milestones=len(milestones),
        completed_tasks=completed_tasks,
        total_tasks=len(tasks),
    )

    growth_response = None

    if growth_assessment:
        growth_response = WorkspaceGrowth.model_validate(
            growth_assessment,
            from_attributes=True,
        )

    return WorkspaceResponse(
        startup=startup_response,
        journey=journey_response,
        validation=validation_response,
        mvp=mvp_response,
        growth=growth_response,
    )

