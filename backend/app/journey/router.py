from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.founder_journey import FounderJourney

from app.journey_schemas import (
    FounderJourneyCreate,
    FounderJourneyUpdate,
    FounderJourneyResponse
)


router = APIRouter(
    prefix="/journey",
    tags=["Founder Journey"]
)


VALID_JOURNEY_TYPES = {
    "NO_IDEA",
    "HAVE_IDEA",
    "EXISTING_STARTUP"
}


# ============================================================
# CREATE JOURNEY
# ============================================================

@router.post(
    "/",
    response_model=FounderJourneyResponse,
    status_code=status.HTTP_201_CREATED
)
def create_journey(
    journey_data: FounderJourneyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    journey_type = journey_data.journey_type.upper()

    if journey_type not in VALID_JOURNEY_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid journey_type. "
                "Use NO_IDEA, HAVE_IDEA, or EXISTING_STARTUP."
            )
        )

    existing_journey = (
        db.query(FounderJourney)
        .filter(
            FounderJourney.user_id == current_user.id
        )
        .first()
    )

    if existing_journey is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Founder journey already exists"
        )

    journey = FounderJourney(
        user_id=current_user.id,
        journey_type=journey_type,
        current_situation=journey_data.current_situation,
        goal=journey_data.goal
    )

    db.add(journey)
    db.commit()
    db.refresh(journey)

    return journey


# ============================================================
# GET CURRENT JOURNEY
# ============================================================

@router.get(
    "/",
    response_model=FounderJourneyResponse
)
def get_journey(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    journey = (
        db.query(FounderJourney)
        .filter(
            FounderJourney.user_id == current_user.id
        )
        .first()
    )

    if journey is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Founder journey not found"
        )

    return journey


# ============================================================
# UPDATE JOURNEY
# ============================================================

@router.put(
    "/",
    response_model=FounderJourneyResponse
)
def update_journey(
    journey_data: FounderJourneyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    journey = (
        db.query(FounderJourney)
        .filter(
            FounderJourney.user_id == current_user.id
        )
        .first()
    )

    if journey is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Founder journey not found"
        )

    update_data = journey_data.model_dump(
        exclude_unset=True
    )

    if "journey_type" in update_data:

        journey_type = update_data["journey_type"].upper()

        if journey_type not in VALID_JOURNEY_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Invalid journey_type. "
                    "Use NO_IDEA, HAVE_IDEA, or EXISTING_STARTUP."
                )
            )

        update_data["journey_type"] = journey_type

    for field, value in update_data.items():
        setattr(journey, field, value)

    db.commit()
    db.refresh(journey)

    return journey