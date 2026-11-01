from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.founder_profile import FounderProfile

from app.founder_profile_schemas import (
    FounderProfileCreate,
    FounderProfileResponse,
    FounderProfileUpdate
)


router = APIRouter(
    prefix="/founder-profile",
    tags=["Founder Profile"]
)


# ============================================================
# CREATE FOUNDER PROFILE
# ============================================================

@router.post(
    "/",
    response_model=FounderProfileResponse,
    status_code=status.HTTP_201_CREATED
)
def create_founder_profile(
    profile_data: FounderProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    existing_profile = (
        db.query(FounderProfile)
        .filter(
            FounderProfile.user_id == current_user.id
        )
        .first()
    )

    if existing_profile is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Founder profile already exists"
        )

    profile = FounderProfile(
        user_id=current_user.id,
        **profile_data.model_dump()
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile


# ============================================================
# GET FOUNDER PROFILE
# ============================================================

@router.get(
    "/",
    response_model=FounderProfileResponse
)
def get_founder_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    profile = (
        db.query(FounderProfile)
        .filter(
            FounderProfile.user_id == current_user.id
        )
        .first()
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Founder profile not found"
        )

    return profile


# ============================================================
# UPDATE FOUNDER PROFILE
# ============================================================

@router.put(
    "/",
    response_model=FounderProfileResponse
)
def update_founder_profile(
    profile_data: FounderProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    profile = (
        db.query(FounderProfile)
        .filter(
            FounderProfile.user_id == current_user.id
        )
        .first()
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Founder profile not found"
        )

    update_data = profile_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    return profile