from app.models.founder_profile import FounderProfile
from app.models.opportunity import Opportunity


# ============================================================
# NORMALIZATION
# ============================================================

TERM_ALIASES = {
    "ai": "artificial intelligence",
    "artificial intelligence": "artificial intelligence",

    "ml": "machine learning",
    "machine learning": "machine learning",

    "nlp": "natural language processing",
    "natural language processing": "natural language processing",

    "api": "api development",
    "api development": "api development",

    "saas": "software as a service",
    "software as a service": "software as a service",

    "edtech": "education technology",
    "education technology": "education technology",

    "web development": "web development",
    "web development": "web development",

    "python": "python",
    "java": "java",
    "sql": "sql",

    "data analytics": "data analytics",
    "data analysis": "data analytics",

    "data engineering": "data engineering",

    "time-series analysis": "time series analysis",
    "time series analysis": "time series analysis",

    "speech recognition": "speech recognition",

    "iot": "iot",
    "iot/data engineering": "iot data engineering",

    "machine learning": "machine learning",
}


def normalize_text(text: str | None) -> str:
    """
    Convert text to lowercase and normalize common
    technology/business terminology.
    """

    if not text:
        return ""

    normalized = text.lower()

    for alias, canonical in TERM_ALIASES.items():
        normalized = normalized.replace(
            alias,
            canonical
        )

    return normalized


def tokenize_requirements(
    text: str | None
) -> list[str]:
    """
    Convert comma-separated requirements into normalized
    individual requirements.
    """

    if not text:
        return []

    items = []

    for item in text.split(","):

        normalized = normalize_text(item).strip()

        if normalized:
            items.append(normalized)

    return items


def contains_concept(
    source: str | None,
    concept: str | None
) -> bool:
    """
    Check whether a normalized concept exists in source text.
    """

    if not source or not concept:
        return False

    source_normalized = normalize_text(source)
    concept_normalized = normalize_text(concept)

    return concept_normalized in source_normalized


# ============================================================
# SKILLS FIT — 20 POINTS
# ============================================================

def calculate_skills_fit(
    profile: FounderProfile,
    opportunity: Opportunity
) -> int:

    founder_skills = tokenize_requirements(
        profile.skills
    )

    required_skills = tokenize_requirements(
        opportunity.required_skills
    )

    if not required_skills:
        return 10

    if not founder_skills:
        return 0

    matched = 0

    for required_skill in required_skills:

        for founder_skill in founder_skills:

            if (
                required_skill in founder_skill
                or founder_skill in required_skill
            ):
                matched += 1
                break

    match_ratio = matched / len(required_skills)

    if match_ratio >= 0.90:
        return 20

    if match_ratio >= 0.75:
        return 17

    if match_ratio >= 0.50:
        return 13

    if match_ratio >= 0.25:
        return 8

    return 3


# ============================================================
# BUDGET FIT — 15 POINTS
# ============================================================

def calculate_budget_fit(
    profile: FounderProfile,
    opportunity: Opportunity
) -> int:

    if profile.budget is None:
        return 5

    if opportunity.estimated_investment is None:
        return 10

    budget = profile.budget
    investment = opportunity.estimated_investment

    if investment <= budget:
        return 15

    if investment <= budget * 1.25:
        return 10

    if investment <= budget * 1.50:
        return 5

    return 0


# ============================================================
# INDUSTRY / INTEREST FIT — 15 POINTS
# ============================================================

def calculate_interest_fit(
    profile: FounderProfile,
    opportunity: Opportunity
) -> int:

    if not profile.interests:
        return 5

    interests = normalize_text(
        profile.interests
    )

    industry = normalize_text(
        opportunity.industry
    )

    description = normalize_text(
        opportunity.description
    )

    # Direct industry match
    if industry and industry in interests:
        return 15

    # Important semantic matches
    if (
        "artificial intelligence" in interests
        and (
            "artificial intelligence" in industry
            or "ai" in industry
        )
    ):
        return 15

    if (
        "education" in interests
        and (
            "education" in industry
            or "edtech" in industry
        )
    ):
        return 15

    if (
        "technology" in interests
        and (
            "technology" in industry
            or "saas" in industry
            or "software" in industry
        )
    ):
        return 12

    # Interest appears in opportunity description
    for interest in [
        "artificial intelligence",
        "education",
        "technology",
        "startups"
    ]:

        if (
            interest in interests
            and interest in description
        ):
            return 10

    return 5


# ============================================================
# EXPERIENCE FIT — 10 POINTS
# ============================================================

def calculate_experience_fit(
    profile: FounderProfile,
    opportunity: Opportunity
) -> int:

    founder_experience = normalize_text(
        profile.experience
    )

    required_experience = normalize_text(
        opportunity.required_experience
    )

    if not required_experience:
        return 10

    if not founder_experience:
        return 0

    # Software development
    software_match = (
        "software development" in required_experience
        and (
            "software development" in founder_experience
            or "web development" in founder_experience
            or "development" in founder_experience
        )
    )

    if software_match:

        # Check for additional domain requirements
        if (
            "education" in required_experience
            and "education" not in founder_experience
        ):
            return 7

        if (
            "industrial" in required_experience
            or "manufacturing" in required_experience
            or "equipment maintenance" in required_experience
        ):
            return 4

        return 10

    # Domain-specific experience
    domain_terms = [
        "education",
        "language learning",
        "language assessment",
        "sales",
        "business analytics",
        "forecasting",
        "customer support",
        "industrial",
        "manufacturing",
        "equipment maintenance"
    ]

    matched_domains = 0

    for term in domain_terms:

        if (
            term in required_experience
            and term in founder_experience
        ):
            matched_domains += 1

    if matched_domains > 0:
        return 10

    # Technical experience is still partially useful
    if (
        "software" in founder_experience
        or "web development" in founder_experience
        or "ai" in founder_experience
    ):
        return 6

    return 3


# ============================================================
# TIME FEASIBILITY — 10 POINTS
# ============================================================

def calculate_time_fit(
    profile: FounderProfile,
    opportunity: Opportunity
) -> int:

    available_time = normalize_text(
        profile.available_time
    )

    difficulty = normalize_text(
        opportunity.difficulty
    )

    if not available_time:
        return 5

    # Current founder has approximately 3 hours/day
    if "3 hours" in available_time:

        if difficulty == "low":
            return 10

        if difficulty == "medium":
            return 8

        if difficulty == "high":
            return 4

    if "2 hours" in available_time:

        if difficulty == "low":
            return 10

        if difficulty == "medium":
            return 7

        return 3

    if "1 hour" in available_time:

        if difficulty == "low":
            return 8

        if difficulty == "medium":
            return 5

        return 2

    return 6


# ============================================================
# GOAL ALIGNMENT — 10 POINTS
# ============================================================

def calculate_goal_alignment(
    profile: FounderProfile,
    opportunity: Opportunity
) -> int:

    goal_text = normalize_text(
        " ".join(
            filter(
                None,
                [
                    profile.short_term_goal,
                    profile.long_term_goal
                ]
            )
        )
    )

    if not goal_text:
        return 5

    description = normalize_text(
        opportunity.description
    )

    goal_concepts = [
        "validate",
        "startup opportunity",
        "technology startup",
        "scalable",
        "technology",
        "build"
    ]

    matched = 0

    for concept in goal_concepts:

        if (
            concept in goal_text
            and concept in description
        ):
            matched += 1

    if matched >= 2:
        return 10

    if matched == 1:
        return 8

    # Technology startups generally align with this founder
    if "technology startup" in goal_text:
        return 8

    return 5


# ============================================================
# RISK COMPATIBILITY — 10 POINTS
# ============================================================

def calculate_risk_fit(
    profile: FounderProfile,
    opportunity: Opportunity
) -> int:

    risk = normalize_text(
        profile.risk_tolerance
    )

    difficulty = normalize_text(
        opportunity.difficulty
    )

    if risk == "low":

        if difficulty == "low":
            return 10

        if difficulty == "medium":
            return 6

        if difficulty == "high":
            return 2

    if risk == "medium":

        if difficulty == "low":
            return 10

        if difficulty == "medium":
            return 9

        if difficulty == "high":
            return 6

    if risk == "high":

        if difficulty == "high":
            return 10

        if difficulty == "medium":
            return 8

        if difficulty == "low":
            return 6

    return 5


# ============================================================
# BUSINESS MODEL FIT — 5 POINTS
# ============================================================

def calculate_business_model_fit(
    profile: FounderProfile,
    opportunity: Opportunity
) -> int:

    preference = normalize_text(
        profile.business_preference
    )

    business_model = normalize_text(
        opportunity.business_model
    )

    if not preference:
        return 3

    if preference == "online":

        # SaaS/subscription/digital products are strong matches
        if (
            "subscription" in business_model
            or "software as a service" in business_model
            or "online" in business_model
            or "platform" in business_model
        ):
            return 5

        return 4

    if preference in business_model:
        return 5

    return 2


# ============================================================
# TEAM FEASIBILITY — 5 POINTS
# ============================================================

def calculate_team_fit(
    profile: FounderProfile,
    opportunity: Opportunity
) -> int:

    team_status = normalize_text(
        profile.team_status
    )

    difficulty = normalize_text(
        opportunity.difficulty
    )

    if "solo" in team_status:

        if difficulty == "low":
            return 5

        if difficulty == "medium":
            return 4

        return 2

    if "small team" in team_status:

        if difficulty == "low":
            return 5

        if difficulty == "medium":
            return 5

        return 4

    return 3


# ============================================================
# FINAL SCORE
# ============================================================

def calculate_opportunity_score(
    profile: FounderProfile,
    opportunity: Opportunity
) -> dict:

    skills_fit = calculate_skills_fit(
        profile,
        opportunity
    )

    budget_fit = calculate_budget_fit(
        profile,
        opportunity
    )

    interest_fit = calculate_interest_fit(
        profile,
        opportunity
    )

    experience_fit = calculate_experience_fit(
        profile,
        opportunity
    )

    time_fit = calculate_time_fit(
        profile,
        opportunity
    )

    goal_alignment = calculate_goal_alignment(
        profile,
        opportunity
    )

    risk_fit = calculate_risk_fit(
        profile,
        opportunity
    )

    business_model_fit = calculate_business_model_fit(
        profile,
        opportunity
    )

    team_fit = calculate_team_fit(
        profile,
        opportunity
    )

    overall_score = (
        skills_fit
        + budget_fit
        + interest_fit
        + experience_fit
        + time_fit
        + goal_alignment
        + risk_fit
        + business_model_fit
        + team_fit
    )

    return {
        "skills_fit": skills_fit,
        "budget_fit": budget_fit,
        "interest_fit": interest_fit,
        "experience_fit": experience_fit,
        "time_fit": time_fit,
        "goal_alignment": goal_alignment,
        "risk_fit": risk_fit,
        "business_model_fit": business_model_fit,
        "team_fit": team_fit,
        "overall_score": overall_score
    }