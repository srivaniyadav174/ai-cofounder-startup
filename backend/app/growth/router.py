from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db

from app.models.user import User
from app.models.startup import Startup
from app.models.founder_journey import FounderJourney
from app.models.growth_assessment import GrowthAssessment

from app.growth.schemas import (
    GrowthAssessmentCreate,
    GrowthAssessmentResponse,
    GrowthSummaryResponse,
)

from app.growth.analyzer import generate_growth_analysis


router = APIRouter(
    prefix="/growth",
    tags=["Growth Engine"],
)


# ============================================================
# HELPERS
# ============================================================

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

    if startup is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup not found.",
        )

    return startup


def require_existing_startup_journey(
    current_user: User,
    db: Session,
) -> FounderJourney:

    journey = (
        db.query(FounderJourney)
        .filter(
            FounderJourney.user_id == current_user.id,
        )
        .first()
    )

    if journey is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Founder journey is required before a growth assessment.",
        )

    if journey.journey_type != "EXISTING_STARTUP":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Growth assessment is available only for the "
                "EXISTING_STARTUP journey."
            ),
        )

    return journey


def get_latest_assessment(
    startup_id: int,
    current_user: User,
    db: Session,
) -> GrowthAssessment | None:

    return (
        db.query(GrowthAssessment)
        .filter(
            GrowthAssessment.startup_id == startup_id,
            GrowthAssessment.founder_id == current_user.id,
        )
        .order_by(
            GrowthAssessment.created_at.desc()
        )
        .first()
    )


# ============================================================
# CREATE GROWTH ASSESSMENT
# ============================================================

@router.post(
    "/{startup_id}/assess",
    response_model=GrowthAssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_growth_assessment(
    startup_id: int,
    assessment_data: GrowthAssessmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    startup = get_owned_startup(
        startup_id,
        current_user,
        db,
    )

    require_existing_startup_journey(
        current_user,
        db,
    )

    assessment = GrowthAssessment(
        founder_id=current_user.id,
        startup_id=startup.id,
        monthly_revenue=assessment_data.monthly_revenue,
        monthly_customers=assessment_data.monthly_customers,
        monthly_growth_percentage=(
            assessment_data.monthly_growth_percentage
        ),
        conversion_rate_percentage=(
            assessment_data.conversion_rate_percentage
        ),
        retention_rate_percentage=(
            assessment_data.retention_rate_percentage
        ),
        churn_rate_percentage=(
            assessment_data.churn_rate_percentage
        ),
        average_revenue_per_customer=(
            assessment_data.average_revenue_per_customer
        ),
        acquisition_channels=(
            assessment_data.acquisition_channels
        ),
        pricing_model=assessment_data.pricing_model,
        sales_process=assessment_data.sales_process,
        competitive_landscape=(
            assessment_data.competitive_landscape
        ),
        current_challenges=(
            assessment_data.current_challenges
        ),
        growth_goal=assessment_data.growth_goal,
        status="ANALYZING",
    )

    db.add(assessment)
    db.flush()

    try:

        analysis = generate_growth_analysis(
            startup=startup,
            assessment=assessment,
        )

    except ValueError as exc:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Unable to generate the growth assessment."
            ),
        ) from exc

    assessment.growth_score = analysis["growth_score"]

    assessment.primary_bottleneck = (
        analysis["primary_bottleneck"]
    )

    assessment.root_causes = "\n".join(
        f"- {item}"
        for item in analysis["root_causes"]
    )

    assessment.growth_opportunities = "\n".join(
        f"- {item}"
        for item in analysis["growth_opportunities"]
    )

    assessment.recommendations = "\n".join(
        f"- {item}"
        for item in analysis["recommendations"]
    )

    action_plan = analysis["action_plan"]

    immediate = action_plan.get(
        "immediate",
        [],
    )

    short_term = action_plan.get(
        "short_term",
        [],
    )

    medium_term = action_plan.get(
        "medium_term",
        [],
    )

    assessment.action_plan = (
        "IMMEDIATE:\n"
        + "\n".join(
            f"- {item}"
            for item in immediate
        )
        + "\n\nSHORT TERM:\n"
        + "\n".join(
            f"- {item}"
            for item in short_term
        )
        + "\n\nMEDIUM TERM:\n"
        + "\n".join(
            f"- {item}"
            for item in medium_term
        )
    )

    assessment.status = "ASSESSED"

    db.commit()
    db.refresh(assessment)

    return assessment


# ============================================================
# GET GROWTH SUMMARY
# IMPORTANT: STATIC ROUTE BEFORE /{startup_id}
# ============================================================

@router.get(
    "/{startup_id}/summary",
    response_model=GrowthSummaryResponse,
)
def get_growth_summary(
    startup_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    startup = get_owned_startup(
        startup_id,
        current_user,
        db,
    )

    assessment = get_latest_assessment(
        startup.id,
        current_user,
        db,
    )

    if assessment is None:

        return GrowthSummaryResponse(
            startup_id=startup.id,
            growth_score=None,
            primary_bottleneck=None,
            assessment_status="NOT_ASSESSED",
            recommendations=None,
            action_plan=None,
            created_at=None,
            updated_at=None,
        )

    return GrowthSummaryResponse(
        startup_id=startup.id,
        growth_score=assessment.growth_score,
        primary_bottleneck=assessment.primary_bottleneck,
        assessment_status=assessment.status,
        recommendations=assessment.recommendations,
        action_plan=assessment.action_plan,
        created_at=assessment.created_at,
        updated_at=assessment.updated_at,
    )


# ============================================================
# GET LATEST GROWTH ASSESSMENT
# ============================================================

@router.get(
    "/{startup_id}",
    response_model=GrowthAssessmentResponse,
)
def get_growth_assessment(
    startup_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    startup = get_owned_startup(
        startup_id,
        current_user,
        db,
    )

    assessment = get_latest_assessment(
        startup.id,
        current_user,
        db,
    )

    if assessment is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No growth assessment exists "
                "for this startup."
            ),
        )

    return assessment