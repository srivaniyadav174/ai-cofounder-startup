import json
import re

from fastapi import APIRouter, Depends, HTTPException, status
from ollama import chat
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db

from app.models.user import User
from app.models.startup import Startup
from app.models.opportunity import Opportunity
from app.models.opportunity_selection import OpportunitySelection
from app.models.validation_experiment import ValidationExperiment
from app.models.validation_decision import ValidationDecision
from app.models.founder_profile import FounderProfile

from app.validation_schemas import (
    ValidationExperimentCreate,
    ValidationExperimentUpdate,
    ValidationExperimentResponse,
    ValidationSummaryResponse,
    ValidationDecisionResponse,
)

from app.validation.decision import (
    generate_validation_decision,
    save_validation_decision,
)


router = APIRouter(
    prefix="/validation",
    tags=["Validation"],
)

OLLAMA_MODEL = "llama3:latest"

VALID_STATUSES = {
    "PLANNED",
    "IN_PROGRESS",
    "COMPLETED",
    "CANCELLED",
}


# ============================================================
# HELPERS
# ============================================================

def get_owned_startup(
    startup_id: int,
    current_user: User,
    db: Session,
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
            detail="Startup not found.",
        )

    return startup


def get_owned_experiment(
    experiment_id: int,
    current_user: User,
    db: Session,
):
    experiment = (
        db.query(ValidationExperiment)
        .filter(
            ValidationExperiment.id == experiment_id,
            ValidationExperiment.founder_id == current_user.id,
        )
        .first()
    )

    if experiment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validation experiment not found.",
        )

    return experiment


def extract_json(text: str):
    """
    Extract JSON from an Ollama response.
    """

    if not text:
        raise ValueError(
            "AI returned an empty response."
        )

    cleaned = text.strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(
            "AI response does not contain valid JSON."
        )

    return json.loads(
        cleaned[start:end + 1]
    )


def normalize_experiment_type(value: str) -> str:

    if not value:
        return "CUSTOMER_INTERVIEW"

    normalized = value.strip().upper()

    aliases = {
        "INTERVIEW": "CUSTOMER_INTERVIEW",
        "CUSTOMER INTERVIEW": "CUSTOMER_INTERVIEW",

        "SURVEY": "SURVEY",

        "LANDING PAGE": "LANDING_PAGE",
        "LANDING_PAGE": "LANDING_PAGE",

        "PROTOTYPE": "PROTOTYPE_TEST",
        "PROTOTYPE TEST": "PROTOTYPE_TEST",

        "CONCIERGE": "CONCIERGE_TEST",
        "CONCIERGE TEST": "CONCIERGE_TEST",

        "PRICING": "PRICING_TEST",
        "PRICING TEST": "PRICING_TEST",

        "COMPETITOR": "COMPETITOR_ANALYSIS",
        "COMPETITOR ANALYSIS": "COMPETITOR_ANALYSIS",
    }

    return aliases.get(
        normalized,
        normalized[:100],
    )


def validate_generated_experiments(data):

    if not isinstance(data, dict):
        raise ValueError(
            "AI response must be a JSON object."
        )

    experiments = data.get("experiments")

    if not isinstance(experiments, list):
        raise ValueError(
            "AI response must contain an experiments list."
        )

    if len(experiments) < 5:
        raise ValueError(
            "AI generated fewer than 5 validation experiments."
        )

    experiments = experiments[:7]

    required_fields = {
        "title",
        "hypothesis",
        "experiment_type",
        "description",
        "success_criteria",
    }

    validated = []

    for index, experiment in enumerate(
        experiments,
        start=1,
    ):

        if not isinstance(experiment, dict):
            raise ValueError(
                f"Experiment {index} is not a valid object."
            )

        missing = required_fields - experiment.keys()

        if missing:
            raise ValueError(
                f"Experiment {index} is missing fields: "
                f"{', '.join(sorted(missing))}"
            )

        for field_name in required_fields:

            value = experiment.get(field_name)

            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"Experiment {index} has invalid "
                    f"{field_name}."
                )

        priority = experiment.get(
            "priority",
            index,
        )

        try:
            priority = int(priority)
        except (TypeError, ValueError):
            priority = index

        priority = max(
            1,
            min(priority, 5),
        )

        validated.append(
            {
                "title": experiment["title"].strip()[:250],

                "hypothesis": (
                    experiment["hypothesis"]
                    .strip()[:3000]
                ),

                "experiment_type": (
                    normalize_experiment_type(
                        experiment["experiment_type"]
                    )
                ),

                "description": (
                    experiment["description"]
                    .strip()[:5000]
                ),

                "success_criteria": (
                    experiment["success_criteria"]
                    .strip()[:3000]
                ),

                "priority": priority,
            }
        )

    return validated


# ============================================================
# AI VALIDATION PLAN GENERATOR
# ============================================================

def generate_validation_experiments(
    startup: Startup,
    opportunity: Opportunity | None,
    founder_context: dict,
):

    opportunity_context = ""

    if opportunity is not None:

        opportunity_context = f"""
SELECTED OPPORTUNITY

Title:
{opportunity.title}

Description:
{opportunity.description}

Industry:
{opportunity.industry}

Required skills:
{opportunity.required_skills}

Required experience:
{opportunity.required_experience}

Target customers:
{opportunity.target_customers}

Business model:
{opportunity.business_model}

Estimated investment:
{opportunity.estimated_investment}

Difficulty:
{opportunity.difficulty}

Market potential:
{opportunity.market_potential}
"""

    prompt = f"""
You are a startup validation strategist.

You are part of an AI-powered startup intelligence
and decision-support platform.

You are NOT a chatbot.

Your job is to design practical experiments that help
a founder determine whether a startup idea should be
continued, changed, or rejected.

The goal is NOT to prove that the idea is good.

The goal is to discover whether important assumptions
are actually true using the cheapest and fastest
realistic experiments.

============================================================
FOUNDER CONTEXT
============================================================

Skills:
{founder_context.get("skills")}

Experience:
{founder_context.get("experience")}

Budget:
{founder_context.get("budget")}

Available time:
{founder_context.get("available_time")}

Interests:
{founder_context.get("interests")}

Preferred industries:
{founder_context.get("preferred_industries")}

Risk tolerance:
{founder_context.get("risk_tolerance")}

Target income:
{founder_context.get("target_income")}

Business preference:
{founder_context.get("business_preference")}

============================================================
SELECTED OPPORTUNITY
============================================================

{opportunity_context}

============================================================
STARTUP
============================================================

Name:
{startup.name}

Description:
{startup.description}

Industry:
{startup.industry}

Stage:
{startup.stage}

Target market:
{startup.target_market}

Business model:
{startup.business_model}

============================================================
VALIDATION PRINCIPLES
============================================================

1. Identify the biggest assumptions behind the startup.

2. Test the problem before spending significant resources
   building the solution.

3. Prefer customer evidence over opinions.

4. Prefer cheap experiments before expensive development.

5. Include willingness-to-pay or pricing validation
   when commercially relevant.

6. Include competitive or differentiation validation.

7. Make success criteria measurable whenever practical.

8. Do not invent market statistics.

9. Do not claim an experiment has already succeeded.

10. Do not assume founder interests are professional
    experience.

11. Keep experiments realistic for the founder's budget
    and available time.

12. Avoid unnecessary regulatory requirements.

13. Experiments should produce useful evidence for a
    later GO / ITERATE / PIVOT decision.

Generate 5 to 7 experiments.

Return ONLY valid JSON.

Required format:

{{
    "experiments": [
        {{
            "title": "...",
            "hypothesis": "...",
            "experiment_type": "CUSTOMER_INTERVIEW",
            "description": "...",
            "success_criteria": "...",
            "priority": 1
        }}
    ]
}}
"""

    try:

        response = chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "AI validation service is unavailable. "
                "Make sure Ollama is running."
            ),
        ) from exc

    try:

        content = response["message"]["content"]

        parsed = extract_json(content)

        return validate_generated_experiments(
            parsed
        )

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "The AI generated an invalid validation "
                "plan. Please try again."
            ),
        ) from exc


# ============================================================
# GENERATE VALIDATION PLAN
# ============================================================

@router.post(
    "/{startup_id}/generate",
    response_model=list[ValidationExperimentResponse],
    status_code=status.HTTP_201_CREATED,
)
def generate_validation_plan(
    startup_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    startup = get_owned_startup(
        startup_id,
        current_user,
        db,
    )

    selection = (
        db.query(OpportunitySelection)
        .filter(
            OpportunitySelection.founder_id
            == current_user.id
        )
        .order_by(
            OpportunitySelection.id.desc()
        )
        .first()
    )

    opportunity = None

    if selection is not None:

        opportunity = (
            db.query(Opportunity)
            .filter(
                Opportunity.id
                == selection.opportunity_id,
                Opportunity.founder_id
                == current_user.id,
            )
            .first()
        )

    founder_profile = (
        db.query(FounderProfile)
        .filter(
            FounderProfile.user_id
            == current_user.id
        )
        .first()
    )

    founder_context = {}

    if founder_profile:

        founder_context = {
            "skills": founder_profile.skills,
            "experience": founder_profile.experience,
            "budget": founder_profile.budget,
            "available_time": (
                founder_profile.available_time
            ),
            "interests": founder_profile.interests,
            "preferred_industries": (
                founder_profile.preferred_industries
            ),
            "risk_tolerance": (
                founder_profile.risk_tolerance
            ),
            "target_income": (
                founder_profile.target_income
            ),
            "business_preference": (
                founder_profile.business_preference
            ),
        }

    existing_count = (
        db.query(ValidationExperiment)
        .filter(
            ValidationExperiment.startup_id
            == startup.id,
            ValidationExperiment.founder_id
            == current_user.id,
        )
        .count()
    )

    if existing_count > 0:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Validation experiments already exist "
                "for this startup."
            ),
        )

    experiments = generate_validation_experiments(
        startup=startup,
        opportunity=opportunity,
        founder_context=founder_context,
    )

    created_experiments = []

    try:

        for experiment_data in experiments:

            experiment = ValidationExperiment(
                founder_id=current_user.id,
                startup_id=startup.id,
                title=experiment_data["title"],
                hypothesis=(
                    experiment_data["hypothesis"]
                ),
                experiment_type=(
                    experiment_data["experiment_type"]
                ),
                description=(
                    experiment_data["description"]
                ),
                success_criteria=(
                    experiment_data["success_criteria"]
                ),
                priority=(
                    experiment_data["priority"]
                ),
                status="PLANNED",
            )

            db.add(experiment)
            created_experiments.append(experiment)

        db.commit()

        for experiment in created_experiments:
            db.refresh(experiment)

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Unable to save the generated "
                "validation plan."
            ),
        ) from exc

    return created_experiments


# ============================================================
# CREATE MANUAL EXPERIMENT
# ============================================================

@router.post(
    "/{startup_id}/experiments",
    response_model=ValidationExperimentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_validation_experiment(
    startup_id: int,
    experiment_data: ValidationExperimentCreate,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    startup = get_owned_startup(
        startup_id,
        current_user,
        db,
    )

    experiment = ValidationExperiment(
        founder_id=current_user.id,
        startup_id=startup.id,
        title=experiment_data.title,
        hypothesis=experiment_data.hypothesis,
        experiment_type=experiment_data.experiment_type,
        description=experiment_data.description,
        success_criteria=experiment_data.success_criteria,
        priority=experiment_data.priority,
    )

    db.add(experiment)
    db.commit()
    db.refresh(experiment)

    return experiment


# ============================================================
# LIST EXPERIMENTS
# ============================================================

@router.get(
    "/{startup_id}/experiments",
    response_model=list[ValidationExperimentResponse],
)
def get_validation_experiments(
    startup_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    startup = get_owned_startup(
        startup_id,
        current_user,
        db,
    )

    return (
        db.query(ValidationExperiment)
        .filter(
            ValidationExperiment.startup_id
            == startup.id,
            ValidationExperiment.founder_id
            == current_user.id,
        )
        .order_by(
            ValidationExperiment.priority.asc(),
            ValidationExperiment.id.asc(),
        )
        .all()
    )


# ============================================================
# GET SINGLE EXPERIMENT
# ============================================================

@router.get(
    "/experiments/{experiment_id}",
    response_model=ValidationExperimentResponse,
)
def get_validation_experiment(
    experiment_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    return get_owned_experiment(
        experiment_id,
        current_user,
        db,
    )


# ============================================================
# UPDATE EXPERIMENT
# ============================================================

@router.put(
    "/experiments/{experiment_id}",
    response_model=ValidationExperimentResponse,
)
def update_validation_experiment(
    experiment_id: int,
    experiment_data: ValidationExperimentUpdate,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    experiment = get_owned_experiment(
        experiment_id,
        current_user,
        db,
    )

    update_data = experiment_data.model_dump(
        exclude_unset=True
    )

    if "status" in update_data:

        new_status = update_data["status"]

        if new_status not in VALID_STATUSES:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Invalid status. Use PLANNED, "
                    "IN_PROGRESS, COMPLETED, or "
                    "CANCELLED."
                ),
            )

    for field, value in update_data.items():
        setattr(
            experiment,
            field,
            value
        )

    db.commit()
    db.refresh(experiment)

    return experiment


# ============================================================
# DELETE EXPERIMENT
# ============================================================

@router.delete(
    "/experiments/{experiment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_validation_experiment(
    experiment_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    experiment = get_owned_experiment(
        experiment_id,
        current_user,
        db,
    )

    db.delete(experiment)
    db.commit()

    return None


# ============================================================
# VALIDATION SUMMARY
# ============================================================

@router.get(
    "/{startup_id}/summary",
    response_model=ValidationSummaryResponse,
)
def get_validation_summary(
    startup_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    startup = get_owned_startup(
        startup_id,
        current_user,
        db,
    )

    experiments = (
        db.query(ValidationExperiment)
        .filter(
            ValidationExperiment.startup_id
            == startup.id,
            ValidationExperiment.founder_id
            == current_user.id,
        )
        .all()
    )

    total = len(experiments)

    planned = sum(
        1
        for experiment in experiments
        if experiment.status == "PLANNED"
    )

    in_progress = sum(
        1
        for experiment in experiments
        if experiment.status == "IN_PROGRESS"
    )

    completed = sum(
        1
        for experiment in experiments
        if experiment.status == "COMPLETED"
    )

    cancelled = sum(
        1
        for experiment in experiments
        if experiment.status == "CANCELLED"
    )

    completed_with_learning = sum(
        1
        for experiment in experiments
        if (
            experiment.status == "COMPLETED"
            and experiment.learning
            and experiment.learning.strip()
        )
    )

    if total == 0:

        recommendation = (
            "Create validation experiments before "
            "deciding whether to build the MVP."
        )

    elif completed == 0:

        recommendation = (
            "Run the planned experiments and record "
            "evidence before making a build decision."
        )

    elif completed_with_learning < completed:

        recommendation = (
            "Complete the learning records for finished "
            "experiments before deciding the next step."
        )

    elif completed >= 3 and completed_with_learning >= 2:

        recommendation = (
            "Enough validation evidence may be available "
            "to define the MVP and decide the next action."
        )

    else:

        recommendation = (
            "Continue validation and gather more evidence "
            "before committing significant resources."
        )

    return ValidationSummaryResponse(
        startup_id=startup.id,
        total_experiments=total,
        planned=planned,
        in_progress=in_progress,
        completed=completed,
        cancelled=cancelled,
        completed_with_learning=(
            completed_with_learning
        ),
        recommendation=recommendation,
    )


# ============================================================
# AI VALIDATION DECISION
# ============================================================

@router.post(
    "/{startup_id}/decision",
    response_model=ValidationDecisionResponse,
)
def create_validation_decision(
    startup_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    startup = get_owned_startup(
        startup_id,
        current_user,
        db,
    )

    # --------------------------------------------------------
    # Only completed experiments with actual evidence
    # --------------------------------------------------------

    experiments = (
        db.query(ValidationExperiment)
        .filter(
            ValidationExperiment.startup_id
            == startup.id,

            ValidationExperiment.founder_id
            == current_user.id,

            ValidationExperiment.status
            == "COMPLETED",
        )
        .order_by(
            ValidationExperiment.priority.asc(),
            ValidationExperiment.id.asc(),
        )
        .all()
    )

    # --------------------------------------------------------
    # Require meaningful evidence
    # --------------------------------------------------------

    if not experiments:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No completed validation experiments "
                "are available. Complete experiments "
                "and record their results before "
                "requesting a validation decision."
            ),
        )

    experiments_with_evidence = [
        experiment
        for experiment in experiments
        if (
            experiment.result
            and experiment.result.strip()
        )
    ]

    if len(experiments_with_evidence) < 2:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "At least 2 completed experiments with "
                "recorded results are required before "
                "generating a validation decision."
            ),
        )

    # --------------------------------------------------------
    # Generate AI decision
    # --------------------------------------------------------

    try:

        decision_data = generate_validation_decision(
            startup=startup,
            experiments=experiments_with_evidence,
        )

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Unable to generate the validation "
                "decision."
            ),
        ) from exc

    # --------------------------------------------------------
    # Save decision
    # --------------------------------------------------------

    try:

        decision = save_validation_decision(
            db=db,
            founder_id=current_user.id,
            startup_id=startup.id,
            decision_data=decision_data,
        )

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "The validation decision was generated "
                "but could not be saved."
            ),
        ) from exc

    return decision
