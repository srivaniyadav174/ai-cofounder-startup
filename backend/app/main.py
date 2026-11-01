
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.auth.dependencies import get_current_user

from app.models.user import User
from app.models.startup import Startup
from app.models.founder_profile import FounderProfile
from app.models.founder_journey import FounderJourney
from app.models.opportunity import Opportunity
from app.models.opportunity_selection import OpportunitySelection
from app.models.validation_experiment import ValidationExperiment
from app.models.validation_decision import ValidationDecision
from app.models.mvp_plan import MVPPlan
from app.models.mvp_milestone import MVPMilestone
from app.models.mvp_task import MVPTask
from app.models.growth_assessment import GrowthAssessment

from app.startup.router import router as startup_router
from app.founder_profile.router import router as founder_profile_router
from app.journey.router import router as journey_router
from app.opportunity.router import router as opportunity_router
from app.opportunity_selection.router import (
    router as opportunity_selection_router
)
from app.validation.router import router as validation_router
from app.ai.router import router as ai_router
from app.mvp.router import router as mvp_router
from app.workspace.router import router as workspace_router
from app.growth.router import router as growth_router


app = FastAPI(
    title="AI Co-Founder",
    description=(
        "AI-powered startup intelligence and "
        "decision-support platform for founders"
    ),
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:5176",
        "http://127.0.0.1:5176",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API ROUTERS
# ============================================================

app.include_router(auth_router)
app.include_router(startup_router)
app.include_router(founder_profile_router)
app.include_router(journey_router)
app.include_router(opportunity_router)
app.include_router(opportunity_selection_router)
app.include_router(validation_router)
app.include_router(ai_router)
app.include_router(mvp_router)
app.include_router(growth_router)
app.include_router(workspace_router)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "AI Co-Founder API is running",
        "version": "1.0.0",
    }


# ============================================================
# CURRENT USER
# ============================================================

@app.get("/auth/me")
def get_me(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
    }
