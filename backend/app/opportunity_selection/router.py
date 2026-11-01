from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db

from app.models.user import User
from app.models.opportunity import Opportunity
from app.models.opportunity_selection import OpportunitySelection
from app.models.founder_journey import FounderJourney
from app.models.startup import Startup

from app.opportunity_selection_schemas import (
    OpportunitySelectionCreate,
    OpportunitySelectionResponse,
    OpportunitySelectionResult,
)


router = APIRouter(
    prefix="/opportunities",
    tags=["Opportunity Selection"],
)


@router.post(
    "/{opportunity_id}/select",
    response_model=OpportunitySelectionResult,
    status_code=201
)
def select_opportunity(
    opportunity_id: int,
    payload: OpportunitySelectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    opportunity = (
        db.query(Opportunity)
        .filter(
            Opportunity.id == opportunity_id,
            Opportunity.founder_id == current_user.id
        )
        .first()
    )

    if not opportunity:
        raise HTTPException(
            status_code=404,
            detail="Opportunity not found"
        )

    journey = (
        db.query(FounderJourney)
        .filter(
            FounderJourney.user_id == current_user.id
        )
        .first()
    )

    if not journey:
        raise HTTPException(
            status_code=404,
            detail="Founder journey not found"
        )

    if journey.journey_type != "NO_IDEA":
        raise HTTPException(
            status_code=400,
            detail=(
                "Opportunity selection is available only "
                "when the founder journey is NO_IDEA."
            )
        )

    existing_selection = (
        db.query(OpportunitySelection)
        .filter(
            OpportunitySelection.founder_id == current_user.id
        )
        .first()
    )

    if existing_selection:
        raise HTTPException(
            status_code=409,
            detail="An opportunity has already been selected."
        )

    startup = Startup(
        founder_id=current_user.id,
        name=opportunity.title,
        description=opportunity.description,
        industry=opportunity.industry,
        stage="Validation",
        target_market=opportunity.target_customers,
        business_model=opportunity.business_model
    )

    selection = OpportunitySelection(
        founder_id=current_user.id,
        opportunity_id=opportunity.id,
        selection_reason=payload.selection_reason
    )

    db.add(selection)
    db.add(startup)

    journey.journey_type = "HAVE_IDEA"

    journey.current_situation = (
        opportunity.title
    )

    journey.goal = (
        "Validate the selected opportunity, "
        "define the MVP, and prepare for launch."
    )

    try:
        db.commit()

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=(
                "Another opportunity selection already exists "
                "for this founder."
            )
        )

    db.refresh(selection)
    db.refresh(startup)
    db.refresh(journey)

    return OpportunitySelectionResult(
        message="Opportunity selected successfully.",
        selection=OpportunitySelectionResponse(
            id=selection.id,
            founder_id=selection.founder_id,
            opportunity_id=selection.opportunity_id,
            selection_reason=selection.selection_reason,
            selected_at=selection.selected_at
        ),
        startup_id=startup.id,
        startup_name=startup.name,
        journey_type=journey.journey_type
    )