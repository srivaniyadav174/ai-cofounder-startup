import re

SKILL_ALIASES = {
    "ai": "artificial intelligence",
    "a.i.": "artificial intelligence",
    "artificial intelligence": "artificial intelligence",
    "ml": "machine learning",
    "m.l.": "machine learning",
    "machine learning": "machine learning",
    "js": "javascript",
    "javascript": "javascript",
    "node": "node.js",
    "nodejs": "node.js",
    "node.js": "node.js",
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "postgres db": "postgresql",
    "sql": "sql",
    "python": "python",
    "java": "java",
    "c++": "c++",
    "cpp": "c++",
    "react": "react",
    "reactjs": "react",
    "react.js": "react",
    "web development": "web development",
    "web dev": "web development",
    "frontend development": "frontend development",
    "front end development": "frontend development",
    "backend development": "backend development",
    "back end development": "backend development",
    "data analysis": "data analysis",
    "data analytics": "data analysis",
    "data science": "data science",
    "deep learning": "deep learning",
    "nlp": "natural language processing",
    "natural language processing": "natural language processing",
    "computer vision": "computer vision",
}


def normalize_skill(skill):
    normalized = str(skill).strip().lower()
    return SKILL_ALIASES.get(normalized, normalized)


def parse_skills(skills_text):
    if not skills_text:
        return set()

    if isinstance(skills_text, list):
        skills = skills_text
    else:
        skills = str(skills_text).split(",")

    return {
        normalize_skill(skill)
        for skill in skills
        if str(skill).strip()
    }


def normalize_text(value):
    if value is None:
        return ""

    return re.sub(r"\s+", " ", str(value).strip().lower())


def calculate_skill_compatibility(founder_skills, required_skills):
    founder_set = parse_skills(founder_skills)
    required_set = parse_skills(required_skills)

    if not required_set:
        return 50

    if not founder_set:
        return 20

    matched = founder_set.intersection(required_set)
    ratio = len(matched) / len(required_set)

    if ratio >= 0.75:
        return 100
    if ratio >= 0.50:
        return 80
    if ratio >= 0.25:
        return 60

    return 30


def calculate_industry_alignment(
    preferred_industries,
    opportunity_industry,
):
    if not opportunity_industry:
        return 50

    if not preferred_industries:
        return 40

    founder_industries = {
        normalize_text(item)
        for item in str(preferred_industries).split(",")
        if item.strip()
    }

    opportunity = normalize_text(opportunity_industry)

    for industry in founder_industries:
        if industry in opportunity or opportunity in industry:
            return 100

    aliases = {
        "ai": {
            "artificial intelligence",
            "machine learning",
            "ai",
        },
        "artificial intelligence": {
            "artificial intelligence",
            "machine learning",
            "ai",
        },
        "machine learning": {
            "machine learning",
            "artificial intelligence",
            "ai",
        },
        "edtech": {
            "education",
            "edtech",
            "educational technology",
        },
        "education": {
            "education",
            "edtech",
            "educational technology",
        },
        "saas": {
            "saas",
            "software as a service",
        },
    }

    for industry in founder_industries:
        related = aliases.get(industry, set())

        if any(item in opportunity for item in related):
            return 90

    return 30


def calculate_budget_compatibility(
    founder_budget,
    estimated_investment,
):
    if estimated_investment is None:
        return 50

    if founder_budget is None:
        return 40

    try:
        founder_budget = float(founder_budget)
        estimated_investment = float(estimated_investment)
    except (TypeError, ValueError):
        return 40

    if estimated_investment <= 0:
        return 70

    if founder_budget <= 0:
        return 20

    ratio = estimated_investment / founder_budget

    if ratio <= 0.25:
        return 100
    if ratio <= 0.50:
        return 90
    if ratio <= 0.75:
        return 80
    if ratio <= 1.00:
        return 70
    if ratio <= 1.50:
        return 50

    return 25


FOUNDER_GENERIC_EXPERIENCE_WORDS = {
    "experience",
    "software",
    "platform",
    "development",
    "developer",
    "technology",
    "technical",
    "application",
    "applications",
    "system",
    "systems",
    "ai",
    "artificial",
    "intelligence",
    "machine",
    "learning",
    "web",
    "online",
    "digital",
}


def extract_meaningful_experience_keywords(text):
    if not text:
        return set()

    words = re.findall(
        r"[a-zA-Z][a-zA-Z0-9+#.-]*",
        str(text).lower(),
    )

    return {
        word
        for word in words
        if len(word) >= 3
        and word not in FOUNDER_GENERIC_EXPERIENCE_WORDS
    }


def calculate_experience_compatibility(
    founder_experience,
    required_experience,
):
    if not required_experience:
        return 50

    if not founder_experience:
        return 30

    founder_keywords = extract_meaningful_experience_keywords(
        founder_experience
    )

    required_keywords = extract_meaningful_experience_keywords(
        required_experience
    )

    if not required_keywords:
        return 50

    matched = founder_keywords.intersection(required_keywords)
    ratio = len(matched) / len(required_keywords)

    if ratio >= 0.75:
        return 100
    if ratio >= 0.50:
        return 80
    if ratio >= 0.25:
        return 60

    return 30


def calculate_time_feasibility(available_time, difficulty):
    time_text = normalize_text(available_time)
    difficulty_text = normalize_text(difficulty)

    if not difficulty_text:
        return 50

    if "easy" in difficulty_text or "low" in difficulty_text:
        return 90

    if "medium" in difficulty_text or "moderate" in difficulty_text:
        if any(
            value in time_text
            for value in ["3 hour", "4 hour", "5 hour", "full time"]
        ):
            return 80

        return 65

    if "hard" in difficulty_text or "high" in difficulty_text:
        if any(
            value in time_text
            for value in ["full time", "8 hour", "6 hour"]
        ):
            return 75

        return 40

    return 50


def calculate_business_preference(
    founder_business_preference,
    opportunity_business_model,
):
    if not founder_business_preference:
        return 50

    if not opportunity_business_model:
        return 50

    preference = normalize_text(founder_business_preference)
    model = normalize_text(opportunity_business_model)

    online_models = [
        "saas",
        "subscription",
        "api",
        "software",
        "online",
        "digital",
        "freemium",
        "license",
        "licensing",
    ]

    offline_models = [
        "local",
        "physical",
        "retail",
        "service",
        "consulting",
    ]

    if "online" in preference:
        if any(item in model for item in online_models):
            return 100

    if "offline" in preference:
        if any(item in model for item in offline_models):
            return 100

    return 50


def calculate_risk_compatibility(
    risk_tolerance,
    difficulty,
):
    risk = normalize_text(risk_tolerance)
    difficulty_text = normalize_text(difficulty)

    if not risk or not difficulty_text:
        return 50

    if risk == "low":
        if "easy" in difficulty_text:
            return 100
        if "medium" in difficulty_text:
            return 70
        if "hard" in difficulty_text:
            return 35

    if risk == "medium":
        if "easy" in difficulty_text:
            return 85
        if "medium" in difficulty_text:
            return 100
        if "hard" in difficulty_text:
            return 65

    if risk == "high":
        if "easy" in difficulty_text:
            return 70
        if "medium" in difficulty_text:
            return 90
        if "hard" in difficulty_text:
            return 100

    return 50


def calculate_goal_alignment(
    short_term_goal,
    long_term_goal,
    opportunity_description,
):
    description = normalize_text(opportunity_description)

    if not description:
        return 40

    goal_text = (
        normalize_text(short_term_goal)
        + " "
        + normalize_text(long_term_goal)
    ).strip()

    if not goal_text:
        return 50

    goal_keywords = set(
        re.findall(
            r"[a-zA-Z][a-zA-Z0-9+#.-]*",
            goal_text,
        )
    )

    description_keywords = set(
        re.findall(
            r"[a-zA-Z][a-zA-Z0-9+#.-]*",
            description,
        )
    )

    if not goal_keywords:
        return 50

    overlap = goal_keywords.intersection(description_keywords)
    ratio = len(overlap) / len(goal_keywords)

    if ratio >= 0.30:
        return 100
    if ratio >= 0.20:
        return 85
    if ratio >= 0.10:
        return 70

    return 50


def calculate_founder_fit_score(
    founder_profile,
    opportunity,
):
    """
    Calculate founder-opportunity compatibility.

    Supports both:
    - SQLAlchemy Opportunity objects
    - AI-generated dictionaries
    """

    def get_field(field_name):
        if isinstance(opportunity, dict):
            return opportunity.get(field_name)

        return getattr(opportunity, field_name, None)

    required_skills = get_field("required_skills")
    industry = get_field("industry")
    estimated_investment = get_field("estimated_investment")
    required_experience = get_field("required_experience")
    difficulty = get_field("difficulty")
    business_model = get_field("business_model")
    description = get_field("description")

    skill_score = calculate_skill_compatibility(
        founder_profile.skills,
        required_skills,
    )

    industry_score = calculate_industry_alignment(
        founder_profile.preferred_industries,
        industry,
    )

    budget_score = calculate_budget_compatibility(
        founder_profile.budget,
        estimated_investment,
    )

    experience_score = calculate_experience_compatibility(
        founder_profile.experience,
        required_experience,
    )

    time_score = calculate_time_feasibility(
        founder_profile.available_time,
        difficulty,
    )

    business_score = calculate_business_preference(
        founder_profile.business_preference,
        business_model,
    )

    risk_score = calculate_risk_compatibility(
        founder_profile.risk_tolerance,
        difficulty,
    )

    goal_score = calculate_goal_alignment(
        founder_profile.short_term_goal,
        founder_profile.long_term_goal,
        description,
    )

    final_score = (
        skill_score * 0.20
        + industry_score * 0.20
        + budget_score * 0.15
        + experience_score * 0.10
        + time_score * 0.10
        + business_score * 0.10
        + risk_score * 0.05
        + goal_score * 0.10
    )

    return {
        "total_score": round(final_score),
        "skills": skill_score,
        "industry": industry_score,
        "budget": budget_score,
        "experience": experience_score,
        "time": time_score,
        "business_preference": business_score,
        "risk": risk_score,
        "goals": goal_score,
    }