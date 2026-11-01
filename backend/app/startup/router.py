from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.startup import Startup


router = APIRouter(
    prefix="/startups",
    tags=["Startups"],
)


class StartupCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: str = Field(..., min_length=1)
    industry: str | None = Field(default=None, max_length=100)
    stage: str | None = Field(default=None, max_length=50)
    target_market: str | None = Field(default=None)
    business_model: str | None = Field(default=None, max_length=100)


class StartupUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = Field(..., min_length=1)
    industry: str | None = Field(default=None, max_length=100)
    stage: str | None = Field(default=None, max_length=50)
    target_market: str | None = None
    business_model: str | None = Field(default=None, max_length=100)


class StartupResponse(BaseModel):
    id: int
    founder_id: int
    name: str
    description: str
    industry: str | None
    stage: str | None
    target_market: str | None
    business_model: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


@router.post(
    "/",
    response_model=StartupResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_startup(
    startup_data: StartupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    startup = Startup(
        founder_id=current_user.id,
        name=startup_data.name,
        description=startup_data.description,
        industry=startup_data.industry,
        stage=startup_data.stage,
        target_market=startup_data.target_market,
        business_model=startup_data.business_model,
    )

    db.add(startup)
    db.commit()
    db.refresh(startup)

    return startup


@router.get(
    "/",
    response_model=list[StartupResponse],
)
def get_startups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    startups = (
        db.query(Startup)
        .filter(
            Startup.founder_id == current_user.id,
        )
        .order_by(Startup.id.asc())
        .all()
    )

    return startups


@router.get(
    "/{startup_id}",
    response_model=StartupResponse,
)
def get_startup(
    startup_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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
            detail="Startup not found",
        )

    return startup


@router.put(
    "/{startup_id}",
    response_model=StartupResponse,
)
def update_startup(
    startup_id: int,
    startup_data: StartupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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
            detail="Startup not found",
        )

    update_data = startup_data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(startup, field, value)

    db.commit()
    db.refresh(startup)

    return startup


@router.delete(
    "/{startup_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_startup(
    startup_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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
            detail="Startup not found",
        )

    db.delete(startup)
    db.commit()

    return None
