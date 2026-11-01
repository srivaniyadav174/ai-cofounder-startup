import json
import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ollama import chat

from app.database import SessionLocal
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.founder_profile import FounderProfile
from app.models.founder_journey import FounderJourney
from app.models.opportunity import Opportunity

from app.opportunity_schemas import (
    OpportunityResponse,
    OpportunityGenerateResponse,
)
from app.opportunity.scoring import calculate_founder_fit_score
from app.opportunity.validator import (
    validate_opportunity,
    validate_opportunity_set,
)


router = APIRouter(
    prefix="/opportunities",
    tags=["Opportunities"],
)


OLLAMA_MODEL = "llama3:latest"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def normalize_list(value):
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        return [
            item.strip()
            for item in value.split(",")
            if item.strip()
        ]

    return [str(value)]


def normalize_string(value):
    if value is None:
        return ""

    return str(value).strip()


def parse_json_response(content: str):
    """
    Extract and parse JSON returned by the local LLM.
    Handles normal JSON and JSON wrapped in markdown fences.
    """

    if not content:
        raise ValueError("AI returned an empty response")

    content = content.strip()

    if content.startswith("```"):
        content = re.sub(
            r"^```(?:json)?\s*",
            "",
            content,
            flags=re.IGNORECASE,
        )
        content = re.sub(
            r"\s*```$",
            "",
            content,
        )

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")

        if start != -1 and end != -1 and end > start:
            return json.loads(content[start:end + 1])

        raise ValueError("AI response was not valid JSON")


def get_founder_context(
    db: Session,
    current_user: User,
):
    founder_profile = (
        db.query(FounderProfile)
        .filter(
            FounderProfile.user_id == current_user.id
        )
        .first()
    )

    journey = (
        db.query(FounderJourney)
        .filter(
            FounderJourney.user_id == current_user.id
        )
        .first()
    )

    if not founder_profile:
        raise HTTPException(
            status_code=400,
            detail="Founder profile is required before generating opportunities.",
        )

    if not journey:
        raise HTTPException(
            status_code=400,
            detail="Founder journey is required before generating opportunities.",
        )

    return founder_profile, journey


@router.post(
    "/generate",
    response_model=OpportunityGenerateResponse,
)
def generate_opportunities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    founder_profile, journey = get_founder_context(
        db,
        current_user,
    )

    if journey.journey_type != "NO_IDEA":
        raise HTTPException(
            status_code=400,
            detail=(
                "Opportunity generation is currently available "
                "for the NO_IDEA journey only."
            ),
        )

    founder_context = {
        "location": founder_profile.location,
        "education": founder_profile.education,
        "skills": founder_profile.skills,
        "experience": founder_profile.experience,
        "available_time": founder_profile.available_time,
        "budget": founder_profile.budget,
        "team_status": founder_profile.team_status,
        "interests": founder_profile.interests,
        "preferred_industries": founder_profile.preferred_industries,
        "business_preference": founder_profile.business_preference,
        "risk_tolerance": founder_profile.risk_tolerance,
        "target_income": founder_profile.target_income,
        "short_term_goal": founder_profile.short_term_goal,
        "long_term_goal": founder_profile.long_term_goal,
        "journey_type": journey.journey_type,
        "current_situation": journey.current_situation,
        "journey_goal": journey.goal,
    }

    prompt = f"""
You are a startup opportunity generation engine inside an
AI startup intelligence platform.

You are NOT a chatbot.

Your job is to generate exactly 5 personalized startup opportunities
for the founder using ONLY the verified founder information below.

CORE PRODUCT PRINCIPLE

The platform adapts to the founder, not the founder to the platform.

The founder currently has NO specific startup idea.

Your task is therefore to discover realistic startup opportunities
that fit this particular founder.

FOUNDER PROFILE

{json.dumps(founder_context, indent=2)}

IMPORTANT FOUNDER FACT RULES

1. Never invent founder experience, qualifications, certifications,
   employment history, customers, revenue, or domain expertise.

2. Do not convert an interest into professional experience.

3. Skills listed in the founder profile may be used as skills.

4. Interests may be used to identify suitable industries or themes,
   but interests are NOT professional experience.

5. Education may be used only as stated.

6. Budget must remain realistic.

7. Available time must be respected.

8. Team status must be respected.

9. Risk tolerance must influence the difficulty and risk of the idea.

10. Target income, short-term goals, and long-term goals should
    influence the recommendations.

11. Do not guarantee revenue, profitability, funding, customers,
    market share, or success.

12. required_experience describes useful experience for operating
    the opportunity. It must not falsely claim that the founder
    already possesses that experience.

13. why_it_fits may mention ONLY verified founder attributes.

HIGH-RISK DOMAIN RESTRICTION

Do not generate opportunities in healthcare, medical diagnosis,
clinical decision-making, legal services, financial advising,
insurance underwriting, or other regulated/high-risk professional
domains unless the founder profile explicitly contains relevant
professional education, qualifications, or operating experience.

The founder's general interest in technology, AI, education, or
startups is NOT evidence of expertise in a regulated domain.

For this founder, prefer technology, AI, SaaS, EdTech, developer
tools, workflow automation, analytics, productivity, and other
lower-risk software opportunities that match the verified founder
profile.

OPPORTUNITY DIVERSITY

Generate exactly 5 substantially different opportunities.

Do NOT generate five variations of the same startup.

The opportunities should differ in at least:

- primary problem
- target customer
- product structure
- business model
- value proposition

Avoid generating multiple versions of:

- generic AI chatbot
- generic recommendation engine
- generic course platform
- generic AI SaaS
- generic productivity application
- generic marketplace

Consider different categories where appropriate:

- B2B software
- B2C software
- AI services
- developer tools
- EdTech
- workflow automation
- analytics
- niche software
- local-business software
- API products
- product infrastructure
- specialized vertical software

BUSINESS MODEL DIVERSITY

Do not make all 5 opportunities subscription businesses.

Across the 5 opportunities, deliberately vary the monetization
model when realistic for the founder.

Possible business models include:

- monthly or annual subscription
- usage-based pricing
- transaction fee
- one-time purchase
- paid implementation or setup
- consulting or AI service
- API usage pricing
- freemium with paid upgrade
- licensing
- per-seat B2B pricing

Do not use the same business model for more than 2 of the 5
opportunities.

Business-model diversity must be genuine.

Do not merely describe the same subscription model using different
words.

BUDGET AND VALIDATION

Respect the founder's stated budget.

Prefer ideas that can be validated before significant investment.

The recommended next step should normally be a practical validation
experiment rather than immediately building a large product.

OUTPUT REQUIREMENTS

Return ONLY valid JSON.

Do not use markdown.

Do not include explanations outside the JSON.

Use exactly this structure:

{{
  "opportunities": [
    {{
      "title": "string",
      "description": "string",
      "industry": "string",
      "required_skills": "string",
      "required_experience": "string",
      "target_customers": "string",
      "business_model": "string",
      "estimated_investment": 0,
      "difficulty": "Easy",
      "market_potential": 1,
      "why_it_fits": "string",
      "risks": "string",
      "recommended_next_step": "string"
    }}
  ]
}}

STRICT FIELD RULES

- opportunities must contain exactly 5 objects.
- title must be unique.
- estimated_investment must be an integer.
- market_potential must be an integer from 1 to 10.
- difficulty must be exactly Easy, Medium, or Hard.
- required_skills must describe genuinely useful skills.
- required_experience must describe useful operating experience,
  not fabricated founder experience.
- why_it_fits must use verified founder information only.
- recommended_next_step must be actionable.
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
            status_code=502,
            detail=f"AI opportunity generation failed: {str(exc)}",
        )

    try:
        content = response["message"]["content"]
        data = parse_json_response(content)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"AI returned invalid opportunity data: {str(exc)}",
        )

    if not isinstance(data, dict):
        raise HTTPException(
            status_code=502,
            detail="AI response must be a JSON object.",
        )

    opportunities = data.get("opportunities")

    if not isinstance(opportunities, list):
        raise HTTPException(
            status_code=502,
            detail="AI response must contain an opportunities list.",
        )

    if len(opportunities) != 5:
        raise HTTPException(
            status_code=502,
            detail=(
                f"AI generated {len(opportunities)} opportunities. "
                "Exactly 5 are required."
            ),
        )

    required_fields = [
        "title",
        "description",
        "industry",
        "required_skills",
        "required_experience",
        "target_customers",
        "business_model",
        "estimated_investment",
        "difficulty",
        "market_potential",
        "why_it_fits",
        "risks",
        "recommended_next_step",
    ]

    titles = []

    for index, opportunity in enumerate(opportunities, start=1):
        if not isinstance(opportunity, dict):
            raise HTTPException(
                status_code=502,
                detail=(
                    f"Opportunity {index} is not a valid JSON object."
                ),
            )

        missing_fields = [
            field
            for field in required_fields
            if field not in opportunity
        ]

        if missing_fields:
            raise HTTPException(
                status_code=502,
                detail=(
                    f"Opportunity {index} is missing fields: "
                    f"{', '.join(missing_fields)}"
                ),
            )

        title = normalize_string(opportunity.get("title"))

        if not title:
            raise HTTPException(
                status_code=502,
                detail=f"Opportunity {index} has an empty title.",
            )

        title_key = title.lower()

        if title_key in titles:
            raise HTTPException(
                status_code=502,
                detail=f"Duplicate opportunity title: {title}",
            )

        titles.append(title_key)

        investment = opportunity.get("estimated_investment")

        if isinstance(investment, bool):
            raise HTTPException(
                status_code=502,
                detail=(
                    f"Opportunity {index} has an invalid "
                    "estimated_investment."
                ),
            )

        if not isinstance(investment, int):
            try:
                investment = int(investment)
                opportunity["estimated_investment"] = investment
            except (TypeError, ValueError):
                raise HTTPException(
                    status_code=502,
                    detail=(
                        f"Opportunity {index} has an invalid "
                        "estimated_investment."
                    ),
                )

        market_potential = opportunity.get("market_potential")

        if isinstance(market_potential, bool):
            raise HTTPException(
                status_code=502,
                detail=(
                    f"Opportunity {index} has an invalid "
                    "market_potential."
                ),
            )

        if not isinstance(market_potential, int):
            try:
                market_potential = int(market_potential)
                opportunity["market_potential"] = market_potential
            except (TypeError, ValueError):
                raise HTTPException(
                    status_code=502,
                    detail=(
                        f"Opportunity {index} has an invalid "
                        "market_potential."
                    ),
                )

        if not 1 <= market_potential <= 10:
            raise HTTPException(
                status_code=502,
                detail=(
                    f"Opportunity {index} has market_potential "
                    "outside the 1-10 range."
                ),
            )

        difficulty = normalize_string(
            opportunity.get("difficulty")
        )

        if difficulty not in {"Easy", "Medium", "Hard"}:
            raise HTTPException(
                status_code=502,
                detail=(
                    f"Opportunity {index} has invalid difficulty: "
                    f"{difficulty}"
                ),
            )

    # Validate every opportunity against the founder profile.
    for index, opportunity in enumerate(opportunities, start=1):
        validation_result = validate_opportunity(
            opportunity,
            founder_profile,
        )

        if validation_result is not True:
            if isinstance(validation_result, str):
                reason = validation_result
            elif isinstance(validation_result, dict):
                reason = validation_result.get(
                    "detail",
                    validation_result.get(
                        "reason",
                        "Opportunity failed validation.",
                    ),
                )
            else:
                reason = "Opportunity failed validation."

            raise HTTPException(
                status_code=502,
                detail=(
                    f"Opportunity {index} failed validation: "
                    f"{reason}"
                ),
            )

    # Validate the complete set for diversity and semantic similarity.
    set_validation_result = validate_opportunity_set(
        opportunities,
        founder_profile,
    )

    if set_validation_result is not True:
        if isinstance(set_validation_result, str):
            reason = set_validation_result
        elif isinstance(set_validation_result, dict):
            reason = set_validation_result.get(
                "detail",
                set_validation_result.get(
                    "reason",
                    "Opportunity set failed validation.",
                ),
            )
        else:
            reason = "Opportunity set failed validation."

        raise HTTPException(
            status_code=502,
            detail=reason,
        )

    # Additional title similarity protection.
    normalized_titles = [
        re.sub(
            r"[^a-z0-9\s]",
            "",
            normalize_string(opportunity["title"]).lower(),
        )
        for opportunity in opportunities
    ]

    for i in range(len(normalized_titles)):
        for j in range(i + 1, len(normalized_titles)):
            words_a = set(normalized_titles[i].split())
            words_b = set(normalized_titles[j].split())

            if not words_a or not words_b:
                continue

            intersection = words_a.intersection(words_b)
            union = words_a.union(words_b)

            similarity = len(intersection) / len(union)

            if similarity >= 0.75:
                raise HTTPException(
                    status_code=502,
                    detail=(
                        "Two opportunity titles are too similar: "
                        f"'{opportunities[i]['title']}' and "
                        f"'{opportunities[j]['title']}'."
                    ),
                )

    # Remove previously generated opportunities for this founder.
    db.query(Opportunity).filter(
        Opportunity.founder_id == current_user.id
    ).delete(
        synchronize_session=False
    )

    db.commit()

    saved_opportunities = []

    for opportunity_data in opportunities:
        opportunity = Opportunity(
            founder_id=current_user.id,
            title=normalize_string(
                opportunity_data["title"]
            ),
            description=normalize_string(
                opportunity_data["description"]
            ),
            industry=normalize_string(
                opportunity_data["industry"]
            ),
            required_skills=normalize_string(
                opportunity_data["required_skills"]
            ),
            required_experience=normalize_string(
                opportunity_data["required_experience"]
            ),
            target_customers=normalize_string(
                opportunity_data["target_customers"]
            ),
            business_model=normalize_string(
                opportunity_data["business_model"]
            ),
            estimated_investment=opportunity_data[
                "estimated_investment"
            ],
            difficulty=normalize_string(
                opportunity_data["difficulty"]
            ),
            market_potential=opportunity_data[
                "market_potential"
            ],
            why_it_fits=normalize_string(
                opportunity_data["why_it_fits"]
            ),
            risks=normalize_string(
                opportunity_data["risks"]
            ),
            recommended_next_step=normalize_string(
                opportunity_data["recommended_next_step"]
            ),
        )

        db.add(opportunity)
        saved_opportunities.append(opportunity)

    db.commit()

    for opportunity in saved_opportunities:
        db.refresh(opportunity)

    response_opportunities = []

    for opportunity in saved_opportunities:
        score_result = calculate_founder_fit_score(
            founder_profile,
            opportunity,
        )

        opportunity.founder_fit_score = score_result[
            "total_score"
        ]

        response_data = {
            "id": opportunity.id,
            "founder_id": opportunity.founder_id,
            "title": opportunity.title,
            "description": opportunity.description,
            "industry": opportunity.industry,
            "required_skills": opportunity.required_skills,
            "required_experience": opportunity.required_experience,
            "target_customers": opportunity.target_customers,
            "business_model": opportunity.business_model,
            "estimated_investment": opportunity.estimated_investment,
            "difficulty": opportunity.difficulty,
            "market_potential": opportunity.market_potential,
            "founder_fit_score": opportunity.founder_fit_score,
            "why_it_fits": opportunity.why_it_fits,
            "risks": opportunity.risks,
            "recommended_next_step": opportunity.recommended_next_step,
            "score_breakdown": score_result,
        }

        response_opportunities.append(response_data)

    db.commit()

    return {
        "message": (
            "Successfully generated 5 personalized "
            "startup opportunities."
        ),
        "opportunities": response_opportunities,
    }


@router.get(
    "/",
    response_model=list[OpportunityResponse],
)
def get_opportunities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    opportunities = (
        db.query(Opportunity)
        .filter(
            Opportunity.founder_id == current_user.id
        )
        .order_by(Opportunity.founder_fit_score.desc())
        .all()
    )

    result = []

    for opportunity in opportunities:
        score_result = calculate_founder_fit_score(
            (
                db.query(FounderProfile)
                .filter(
                    FounderProfile.user_id == current_user.id
                )
                .first()
            ),
            opportunity,
        )

        result.append(
            {
                "id": opportunity.id,
                "founder_id": opportunity.founder_id,
                "title": opportunity.title,
                "description": opportunity.description,
                "industry": opportunity.industry,
                "required_skills": opportunity.required_skills,
                "required_experience": opportunity.required_experience,
                "target_customers": opportunity.target_customers,
                "business_model": opportunity.business_model,
                "estimated_investment": opportunity.estimated_investment,
                "difficulty": opportunity.difficulty,
                "market_potential": opportunity.market_potential,
                "founder_fit_score": opportunity.founder_fit_score,
                "why_it_fits": opportunity.why_it_fits,
                "risks": opportunity.risks,
                "recommended_next_step": opportunity.recommended_next_step,
                "score_breakdown": score_result,
            }
        )

    return result


@router.get(
    "/{opportunity_id}",
    response_model=OpportunityResponse,
)
def get_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    opportunity = (
        db.query(Opportunity)
        .filter(
            Opportunity.id == opportunity_id,
            Opportunity.founder_id == current_user.id,
        )
        .first()
    )

    if not opportunity:
        raise HTTPException(
            status_code=404,
            detail="Opportunity not found.",
        )

    founder_profile = (
        db.query(FounderProfile)
        .filter(
            FounderProfile.user_id == current_user.id
        )
        .first()
    )

    score_result = calculate_founder_fit_score(
        founder_profile,
        opportunity,
    )

    return {
        "id": opportunity.id,
        "founder_id": opportunity.founder_id,
        "title": opportunity.title,
        "description": opportunity.description,
        "industry": opportunity.industry,
        "required_skills": opportunity.required_skills,
        "required_experience": opportunity.required_experience,
        "target_customers": opportunity.target_customers,
        "business_model": opportunity.business_model,
        "estimated_investment": opportunity.estimated_investment,
        "difficulty": opportunity.difficulty,
        "market_potential": opportunity.market_potential,
        "founder_fit_score": opportunity.founder_fit_score,
        "why_it_fits": opportunity.why_it_fits,
        "risks": opportunity.risks,
        "recommended_next_step": opportunity.recommended_next_step,
        "score_breakdown": score_result,
    }