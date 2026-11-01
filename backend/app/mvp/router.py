from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db

from app.models.user import User
from app.models.startup import Startup
from app.models.validation_decision import ValidationDecision
from app.models.validation_experiment import ValidationExperiment
from app.models.mvp_plan import MVPPlan
from app.models.mvp_milestone import MVPMilestone
from app.models.mvp_task import MVPTask

from app.mvp.generator import generate_mvp_plan


router = APIRouter(
    prefix="/mvp",
    tags=["MVP"]
)


# ============================================================
# HELPERS
# ============================================================

def get_owned_startup(
    startup_id: int,
    current_user: User,
    db: Session
) -> Startup:

    startup = (
        db.query(Startup)
        .filter(
            Startup.id == startup_id,
            Startup.founder_id == current_user.id
        )
        .first()
    )

    if not startup:
        raise HTTPException(
            status_code=404,
            detail="Startup not found"
        )

    return startup


def get_latest_decision(
    startup_id: int,
    current_user: User,
    db: Session
) -> ValidationDecision:

    decision = (
        db.query(ValidationDecision)
        .filter(
            ValidationDecision.startup_id == startup_id,
            ValidationDecision.founder_id == current_user.id
        )
        .order_by(
            ValidationDecision.created_at.desc()
        )
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail=(
                "No validation decision exists "
                "for this startup"
            )
        )

    return decision


def get_owned_mvp_plan(
    plan_id: int,
    current_user: User,
    db: Session
) -> MVPPlan:

    plan = (
        db.query(MVPPlan)
        .join(
            Startup,
            Startup.id == MVPPlan.startup_id
        )
        .filter(
            MVPPlan.id == plan_id,
            MVPPlan.founder_id == current_user.id,
            Startup.founder_id == current_user.id
        )
        .first()
    )

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="MVP plan not found"
        )

    return plan


def get_owned_milestone(
    milestone_id: int,
    current_user: User,
    db: Session
) -> MVPMilestone:

    milestone = (
        db.query(MVPMilestone)
        .join(
            MVPPlan,
            MVPPlan.id == MVPMilestone.mvp_plan_id
        )
        .join(
            Startup,
            Startup.id == MVPMilestone.startup_id
        )
        .filter(
            MVPMilestone.id == milestone_id,
            MVPMilestone.founder_id == current_user.id,
            MVPPlan.founder_id == current_user.id,
            Startup.founder_id == current_user.id,
            MVPPlan.startup_id == MVPMilestone.startup_id
        )
        .first()
    )

    if not milestone:
        raise HTTPException(
            status_code=404,
            detail="Milestone not found"
        )

    return milestone


def get_owned_task(
    task_id: int,
    current_user: User,
    db: Session
) -> MVPTask:

    task = (
        db.query(MVPTask)
        .join(
            MVPPlan,
            MVPPlan.id == MVPTask.mvp_plan_id
        )
        .join(
            Startup,
            Startup.id == MVPTask.startup_id
        )
        .filter(
            MVPTask.id == task_id,
            MVPTask.founder_id == current_user.id,
            MVPPlan.founder_id == current_user.id,
            Startup.founder_id == current_user.id,
            MVPPlan.startup_id == MVPTask.startup_id
        )
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="MVP task not found"
        )

    if task.milestone_id is not None:

        milestone = (
            db.query(MVPMilestone)
            .filter(
                MVPMilestone.id == task.milestone_id,
                MVPMilestone.mvp_plan_id == task.mvp_plan_id,
                MVPMilestone.startup_id == task.startup_id,
                MVPMilestone.founder_id == current_user.id
            )
            .first()
        )

        if milestone is None:
            raise HTTPException(
                status_code=404,
                detail="MVP task hierarchy is invalid"
            )

    return task


# ============================================================
# GENERATE MVP
# ============================================================

@router.post("/{startup_id}/generate")
def generate_mvp(
    startup_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    startup = get_owned_startup(
        startup_id,
        current_user,
        db
    )

    decision = get_latest_decision(
        startup_id,
        current_user,
        db
    )

    if decision.decision != "PROCEED_TO_MVP":

        raise HTTPException(
            status_code=409,
            detail=(
                "MVP planning is only available when "
                "the latest validation decision is "
                "PROCEED_TO_MVP. "
                f"Current decision: {decision.decision}"
            )
        )

    experiments = (
        db.query(ValidationExperiment)
        .filter(
            ValidationExperiment.startup_id == startup_id,
            ValidationExperiment.founder_id == current_user.id,
            ValidationExperiment.status == "COMPLETED",
            ValidationExperiment.result.isnot(None)
        )
        .order_by(
            ValidationExperiment.created_at.asc()
        )
        .all()
    )

    if len(experiments) < 2:

        raise HTTPException(
            status_code=422,
            detail=(
                "At least 2 completed validation "
                "experiments with results are required "
                "before generating an MVP plan."
            )
        )

    try:

        generated = generate_mvp_plan(
            startup=startup,
            decision=decision,
            experiments=experiments
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=502,
            detail=f"AI returned invalid MVP data: {exc}"
        ) from exc

    except RuntimeError as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc)
        ) from exc

    previous_plans = (
        db.query(MVPPlan)
        .filter(
            MVPPlan.startup_id == startup_id,
            MVPPlan.founder_id == current_user.id
        )
        .all()
    )

    try:

        for previous_plan in previous_plans:

            db.query(MVPTask).filter(
                MVPTask.mvp_plan_id == previous_plan.id
            ).delete(
                synchronize_session=False
            )

            db.query(MVPMilestone).filter(
                MVPMilestone.mvp_plan_id == previous_plan.id
            ).delete(
                synchronize_session=False
            )

            db.delete(previous_plan)

        db.flush()

        plan = MVPPlan(
            founder_id=current_user.id,
            startup_id=startup.id,
            validation_decision_id=decision.id,
            title=generated["title"],
            objective=generated["objective"],
            problem_to_solve=generated["problem_to_solve"],
            target_customer=generated["target_customer"],
            core_value_proposition=generated[
                "core_value_proposition"
            ],
            scope=generated["scope"],
            out_of_scope=generated.get("out_of_scope"),
            success_metrics=generated["success_metrics"],
            estimated_duration_days=int(
                generated["estimated_duration_days"]
            ),
            status="PLANNED"
        )

        db.add(plan)
        db.flush()

        for milestone_data in generated["milestones"]:

            milestone = MVPMilestone(
                founder_id=current_user.id,
                startup_id=startup.id,
                mvp_plan_id=plan.id,
                title=milestone_data["title"],
                description=milestone_data["description"],
                order_index=int(
                    milestone_data["order_index"]
                ),
                status="NOT_STARTED",
                target_days=int(
                    milestone_data["target_days"]
                )
            )

            db.add(milestone)
            db.flush()

            for task_data in milestone_data["tasks"]:

                task = MVPTask(
                    founder_id=current_user.id,
                    startup_id=startup.id,
                    mvp_plan_id=plan.id,
                    milestone_id=milestone.id,
                    title=task_data["title"],
                    description=task_data["description"],
                    priority=int(task_data["priority"]),
                    estimated_hours=(
                        int(task_data["estimated_hours"])
                        if task_data.get("estimated_hours") is not None
                        else None
                    ),
                    status="TODO",
                    due_days=(
                        int(task_data["due_days"])
                        if task_data.get("due_days") is not None
                        else None
                    )
                )

                db.add(task)

        db.commit()
        db.refresh(plan)

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to save the MVP plan."
        )

    return {
        "message": "MVP plan generated successfully",
        "startup_id": startup.id,
        "startup_name": startup.name,
        "validation_decision": decision.decision,
        "validation_confidence": decision.confidence_score,
        "mvp_plan_id": plan.id
    }


# ============================================================
# GET MVP PLAN
# ============================================================

@router.get("/{startup_id}")
def get_mvp_plan(
    startup_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    startup = get_owned_startup(
        startup_id,
        current_user,
        db
    )

    plan = (
        db.query(MVPPlan)
        .filter(
            MVPPlan.startup_id == startup.id,
            MVPPlan.founder_id == current_user.id
        )
        .order_by(
            MVPPlan.created_at.desc()
        )
        .first()
    )

    if not plan:

        raise HTTPException(
            status_code=404,
            detail="MVP plan not found"
        )

    milestones = (
        db.query(MVPMilestone)
        .filter(
            MVPMilestone.mvp_plan_id == plan.id,
            MVPMilestone.founder_id == current_user.id,
            MVPMilestone.startup_id == startup.id
        )
        .order_by(
            MVPMilestone.order_index.asc()
        )
        .all()
    )

    result_milestones = []

    for milestone in milestones:

        tasks = (
            db.query(MVPTask)
            .filter(
                MVPTask.milestone_id == milestone.id,
                MVPTask.mvp_plan_id == plan.id,
                MVPTask.founder_id == current_user.id,
                MVPTask.startup_id == startup.id
            )
            .order_by(
                MVPTask.priority.asc(),
                MVPTask.id.asc()
            )
            .all()
        )

        result_milestones.append(
            {
                "id": milestone.id,
                "title": milestone.title,
                "description": milestone.description,
                "order_index": milestone.order_index,
                "status": milestone.status,
                "target_days": milestone.target_days,
                "tasks": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "priority": task.priority,
                        "estimated_hours": task.estimated_hours,
                        "status": task.status,
                        "due_days": task.due_days
                    }
                    for task in tasks
                ]
            }
        )

    return {
        "startup_id": startup.id,
        "startup_name": startup.name,
        "mvp_plan": {
            "id": plan.id,
            "title": plan.title,
            "objective": plan.objective,
            "problem_to_solve": plan.problem_to_solve,
            "target_customer": plan.target_customer,
            "core_value_proposition": plan.core_value_proposition,
            "scope": plan.scope,
            "out_of_scope": plan.out_of_scope,
            "success_metrics": plan.success_metrics,
            "estimated_duration_days": plan.estimated_duration_days,
            "status": plan.status,
            "created_at": plan.created_at,
            "updated_at": plan.updated_at
        },
        "milestones": result_milestones
    }


# ============================================================
# UPDATE MVP STATUS
# ============================================================

@router.patch("/{startup_id}/status")
def update_mvp_status(
    startup_id: int,
    status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    startup = get_owned_startup(
        startup_id,
        current_user,
        db
    )

    plan = (
        db.query(MVPPlan)
        .filter(
            MVPPlan.startup_id == startup.id,
            MVPPlan.founder_id == current_user.id
        )
        .order_by(
            MVPPlan.created_at.desc()
        )
        .first()
    )

    if not plan:

        raise HTTPException(
            status_code=404,
            detail="MVP plan not found"
        )

    allowed_statuses = {
        "PLANNED",
        "IN_PROGRESS",
        "COMPLETED",
        "CANCELLED"
    }

    normalized_status = status.strip().upper()

    if normalized_status not in allowed_statuses:

        raise HTTPException(
            status_code=422,
            detail=(
                "Invalid MVP status. Allowed values: "
                "PLANNED, IN_PROGRESS, COMPLETED, "
                "CANCELLED"
            )
        )

    plan.status = normalized_status

    db.commit()
    db.refresh(plan)

    return {
        "message": "MVP plan status updated",
        "mvp_plan_id": plan.id,
        "status": plan.status
    }


# ============================================================
# UPDATE MILESTONE STATUS
# ============================================================

@router.patch("/milestones/{milestone_id}/status")
def update_milestone_status(
    milestone_id: int,
    status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    milestone = get_owned_milestone(
        milestone_id,
        current_user,
        db
    )

    allowed_statuses = {
        "NOT_STARTED",
        "IN_PROGRESS",
        "COMPLETED"
    }

    normalized_status = status.strip().upper()

    if normalized_status not in allowed_statuses:

        raise HTTPException(
            status_code=422,
            detail=(
                "Invalid milestone status. Allowed values: "
                "NOT_STARTED, IN_PROGRESS, COMPLETED"
            )
        )

    milestone.status = normalized_status

    db.commit()
    db.refresh(milestone)

    return {
        "message": "Milestone status updated",
        "milestone_id": milestone.id,
        "status": milestone.status
    }


# ============================================================
# UPDATE TASK STATUS
# ============================================================

@router.patch("/tasks/{task_id}/status")
def update_task_status(
    task_id: int,
    status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    task = get_owned_task(
        task_id,
        current_user,
        db
    )

    allowed_statuses = {
        "TODO",
        "IN_PROGRESS",
        "COMPLETED",
        "BLOCKED"
    }

    normalized_status = status.strip().upper()

    if normalized_status not in allowed_statuses:

        raise HTTPException(
            status_code=422,
            detail=(
                "Invalid task status. Allowed values: "
                "TODO, IN_PROGRESS, COMPLETED, BLOCKED"
            )
        )

    task.status = normalized_status

    db.commit()
    db.refresh(task)

    return {
        "message": "MVP task status updated",
        "task_id": task.id,
        "status": task.status
    }


# ============================================================
# MVP PROGRESS
# ============================================================

@router.get("/{startup_id}/progress")
def get_mvp_progress(
    startup_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    startup = get_owned_startup(
        startup_id,
        current_user,
        db
    )

    plan = (
        db.query(MVPPlan)
        .filter(
            MVPPlan.startup_id == startup.id,
            MVPPlan.founder_id == current_user.id
        )
        .order_by(
            MVPPlan.created_at.desc()
        )
        .first()
    )

    if not plan:

        raise HTTPException(
            status_code=404,
            detail="MVP plan not found"
        )

    tasks = (
        db.query(MVPTask)
        .filter(
            MVPTask.mvp_plan_id == plan.id,
            MVPTask.founder_id == current_user.id,
            MVPTask.startup_id == startup.id
        )
        .all()
    )

    milestones = (
        db.query(MVPMilestone)
        .filter(
            MVPMilestone.mvp_plan_id == plan.id,
            MVPMilestone.founder_id == current_user.id,
            MVPMilestone.startup_id == startup.id
        )
        .all()
    )

    total_tasks = len(tasks)

    completed_tasks = sum(
        1
        for task in tasks
        if task.status == "COMPLETED"
    )

    total_milestones = len(milestones)

    completed_milestones = sum(
        1
        for milestone in milestones
        if milestone.status == "COMPLETED"
    )

    task_progress = (
        round(
            completed_tasks / total_tasks * 100,
            2
        )
        if total_tasks
        else 0
    )

    milestone_progress = (
        round(
            completed_milestones / total_milestones * 100,
            2
        )
        if total_milestones
        else 0
    )

    return {
        "startup_id": startup.id,
        "mvp_plan_id": plan.id,
        "mvp_status": plan.status,
        "tasks": {
            "total": total_tasks,
            "completed": completed_tasks,
            "progress_percentage": task_progress
        },
        "milestones": {
            "total": total_milestones,
            "completed": completed_milestones,
            "progress_percentage": milestone_progress
        }
    }