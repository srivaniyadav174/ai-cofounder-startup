import re


# =========================================================
# Generic helpers
# =========================================================

def normalize_text(value: str | None) -> str:
    """Normalize text for comparison."""

    if not value:
        return ""

    value = str(value).lower()
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def text_contains_any(
    text: str | None,
    keywords: set[str],
) -> bool:
    """Check whether text contains any keyword."""

    normalized = normalize_text(text)

    return any(
        normalize_text(keyword) in normalized
        for keyword in keywords
    )


def calculate_word_similarity(
    text_a: str | None,
    text_b: str | None,
) -> float:
    """Calculate Jaccard similarity between two texts."""

    words_a = set(
        normalize_text(text_a).split()
    )

    words_b = set(
        normalize_text(text_b).split()
    )

    if not words_a or not words_b:
        return 0.0

    intersection = words_a.intersection(words_b)
    union = words_a.union(words_b)

    if not union:
        return 0.0

    return len(intersection) / len(union)


# =========================================================
# Founder evidence
# =========================================================

FOUNDER_GENERIC_WORDS = {
    "experience",
    "student",
    "internship",
    "project",
    "projects",
    "technology",
    "technical",
    "software",
    "development",
    "developer",
    "application",
    "applications",
    "system",
    "systems",
    "platform",
    "ai",
    "artificial",
    "intelligence",
    "machine",
    "learning",
    "web",
    "online",
    "digital",
    "computer",
    "science",
    "engineering",
}


def get_founder_evidence(
    founder_profile,
) -> set[str]:
    """
    Extract meaningful evidence from the founder profile.

    Generic words are removed so that words such as
    'student', 'technology', and 'AI' do not count as
    specialized domain evidence.
    """

    profile_text = " ".join(
        [
            founder_profile.skills or "",
            founder_profile.experience or "",
            founder_profile.interests or "",
            founder_profile.preferred_industries or "",
            founder_profile.education or "",
        ]
    )

    words = set(
        normalize_text(profile_text).split()
    )

    return {
        word
        for word in words
        if len(word) > 2
        and word not in FOUNDER_GENERIC_WORDS
    }


# =========================================================
# Unsupported founder claims
# =========================================================

FOUNDER_CLAIM_PATTERNS = [
    "your experience in",
    "your experience with",
    "your background in",
    "your background with",
    "your expertise in",
    "your expertise with",
    "you have experience in",
    "you have experience with",
    "you have a background in",
    "you have a background with",
    "your knowledge of",
    "your knowledge in",
    "your work with",
    "you worked with",
]


def extract_claimed_domain(
    text: str | None,
) -> str | None:
    """
    Extract the text following a founder-experience
    claim phrase.
    """

    normalized = normalize_text(text)

    for pattern in FOUNDER_CLAIM_PATTERNS:

        if pattern in normalized:

            remaining = normalized.split(
                pattern,
                1,
            )[1]

            return remaining.strip()

    return None


def contains_unsupported_founder_claim(
    text: str | None,
    founder_profile,
) -> bool:
    """
    Detect claims that the founder has experience in
    a specialized domain not supported by the profile.
    """

    if not text:
        return False

    claimed_domain = extract_claimed_domain(text)

    if not claimed_domain:
        return False

    founder_evidence = get_founder_evidence(
        founder_profile
    )

    claimed_words = set(
        claimed_domain.split()
    )

    claimed_words = {
        word
        for word in claimed_words
        if len(word) > 2
        and word not in FOUNDER_GENERIC_WORDS
    }

    if not claimed_words:
        return False

    overlap = claimed_words.intersection(
        founder_evidence
    )

    return len(overlap) == 0


# =========================================================
# High-risk domains
# =========================================================

HIGH_RISK_DOMAINS = {
    "healthcare": {
        "healthcare",
        "health",
        "medical",
        "medicine",
        "hospital",
        "clinical",
        "patient",
        "diagnosis",
        "treatment",
        "symptom",
        "mental health",
    },

    "finance": {
        "finance",
        "financial",
        "banking",
        "investment",
        "trading",
        "insurance",
        "loan",
        "lending",
        "credit",
        "wealth",
    },

    "legal": {
        "legal",
        "law",
        "lawyer",
        "attorney",
        "court",
        "litigation",
        "compliance",
    },
}


def detect_high_risk_domain(
    industry: str | None,
    description: str | None,
    target_customers: str | None,
) -> str | None:
    """Detect high-risk domains."""

    combined_text = " ".join(
        [
            industry or "",
            description or "",
            target_customers or "",
        ]
    )

    normalized = normalize_text(combined_text)

    for domain, keywords in HIGH_RISK_DOMAINS.items():

        for keyword in keywords:

            normalized_keyword = normalize_text(
                keyword
            )

            if normalized_keyword in normalized:
                return domain

    return None


# =========================================================
# High-risk capabilities
# =========================================================

HIGH_RISK_CAPABILITIES = {
    "healthcare": {
        "diagnosis",
        "treatment recommendation",
        "treatment recommendations",
        "medical advice",
        "medical diagnosis",
        "symptom diagnosis",
        "prescription",
        "clinical decision",
    },

    "finance": {
        "investment advice",
        "financial advice",
        "trading recommendation",
        "loan approval",
        "credit decision",
    },

    "legal": {
        "legal advice",
        "legal recommendation",
        "case prediction",
        "court recommendation",
    },
}


def detect_high_risk_capability(
    description: str | None,
    target_customers: str | None,
) -> str | None:
    """Detect high-risk professional capabilities."""

    combined_text = " ".join(
        [
            description or "",
            target_customers or "",
        ]
    )

    normalized = normalize_text(combined_text)

    for domain, capabilities in (
        HIGH_RISK_CAPABILITIES.items()
    ):

        for capability in capabilities:

            normalized_capability = normalize_text(
                capability
            )

            if normalized_capability in normalized:
                return domain

    return None


# =========================================================
# Required experience validation
# =========================================================

def required_experience_copies_founder(
    founder_experience: str | None,
    required_experience: str | None,
) -> bool:
    """
    Required experience may overlap with the founder's
    experience.

    This is not considered a validation failure.

    Unsupported claims about founder expertise are handled
    separately by contains_unsupported_founder_claim().
    """

    return False


# =========================================================
# Business model normalization
# =========================================================

def normalize_business_model(
    business_model: str | None,
) -> str:
    """Convert a business model into a broad category."""

    normalized = normalize_text(
        business_model
    )

    if any(
        word in normalized
        for word in [
            "subscription",
            "monthly",
            "annual plan",
            "saas",
        ]
    ):
        return "subscription"

    if any(
        word in normalized
        for word in [
            "commission",
            "transaction fee",
            "transaction fees",
            "marketplace fee",
        ]
    ):
        return "transaction"

    if any(
        word in normalized
        for word in [
            "usage based",
            "pay per use",
            "per usage",
            "api pricing",
        ]
    ):
        return "usage"

    if any(
        word in normalized
        for word in [
            "consulting",
            "consultancy",
            "service",
            "services",
            "implementation",
            "setup fee",
            "paid setup",
        ]
    ):
        return "service"

    if any(
        word in normalized
        for word in [
            "licensing",
            "license",
            "enterprise license",
        ]
    ):
        return "licensing"

    if any(
        word in normalized
        for word in [
            "freemium",
            "free tier",
        ]
    ):
        return "freemium"

    if any(
        word in normalized
        for word in [
            "one time",
            "one time purchase",
            "one off",
            "one off purchase",
        ]
    ):
        return "one_time"

    if any(
        word in normalized
        for word in [
            "per seat",
            "per user",
            "per employee",
        ]
    ):
        return "per_seat"

    return "other"


# =========================================================
# Opportunity semantic similarity
# =========================================================

GENERIC_OPPORTUNITY_WORDS = {
    "ai",
    "powered",
    "driven",
    "enabled",
    "platform",
    "system",
    "tool",
    "solution",
    "online",
    "smart",
    "digital",
    "software",
    "application",
    "app",
    "technology",
    "machine",
    "learning",
}


def meaningful_opportunity_words(
    value: str | None,
) -> set[str]:
    """Extract meaningful opportunity words."""

    words = set(
        normalize_text(value).split()
    )

    return {
        word
        for word in words
        if len(word) > 2
        and word not in GENERIC_OPPORTUNITY_WORDS
    }


def calculate_opportunity_similarity(
    opportunity_a: dict,
    opportunity_b: dict,
) -> float:
    """
    Compare two opportunities using title,
    description, target customers, and industry.
    """

    text_a = " ".join(
        [
            opportunity_a.get("title", ""),
            opportunity_a.get("description", ""),
            opportunity_a.get("target_customers", ""),
            opportunity_a.get("industry", ""),
        ]
    )

    text_b = " ".join(
        [
            opportunity_b.get("title", ""),
            opportunity_b.get("description", ""),
            opportunity_b.get("target_customers", ""),
            opportunity_b.get("industry", ""),
        ]
    )

    words_a = meaningful_opportunity_words(text_a)
    words_b = meaningful_opportunity_words(text_b)

    if not words_a or not words_b:
        return 0.0

    intersection = words_a.intersection(words_b)
    union = words_a.union(words_b)

    if not union:
        return 0.0

    return len(intersection) / len(union)


# =========================================================
# Validate one opportunity
# =========================================================

def validate_opportunity(
    opportunity: dict,
    founder_profile,
) -> bool | str:
    """
    Validate one AI-generated opportunity.

    Returns:
        True
            when valid.

        str
            containing the exact validation failure reason.
    """

    title = opportunity.get("title")
    description = opportunity.get("description")
    industry = opportunity.get("industry")
    target_customers = opportunity.get("target_customers")
    required_experience = opportunity.get(
        "required_experience"
    )
    business_model = opportunity.get("business_model")
    why_it_fits = opportunity.get("why_it_fits")

    # -----------------------------------------------------
    # 1. Basic fields
    # -----------------------------------------------------

    if not title or not str(title).strip():
        return "Opportunity title is empty."

    if not description or not str(description).strip():
        return "Opportunity description is empty."

    if not industry or not str(industry).strip():
        return "Opportunity industry is empty."

    if not target_customers or not str(
        target_customers
    ).strip():
        return "Opportunity target_customers is empty."

    # -----------------------------------------------------
    # 2. High-risk domain
    # -----------------------------------------------------

    high_risk_domain = detect_high_risk_domain(
        industry,
        description,
        target_customers,
    )

    if high_risk_domain:

        founder_evidence = get_founder_evidence(
            founder_profile
        )

        domain_words = HIGH_RISK_DOMAINS[
            high_risk_domain
        ]

        # Normalize multi-word domain phrases into
        # individual meaningful terms.
        domain_tokens = set()

        for domain_word in domain_words:

            normalized_domain_word = normalize_text(
                domain_word
            )

            for token in normalized_domain_word.split():

                if (
                    len(token) > 3
                    and token not in FOUNDER_GENERIC_WORDS
                ):
                    domain_tokens.add(token)

        has_domain_evidence = any(
            token in founder_evidence
            for token in domain_tokens
        )

        if not has_domain_evidence:

            return (
                "High-risk domain detected "
                f"({high_risk_domain}) without relevant "
                "founder evidence."
            )

    # -----------------------------------------------------
    # 3. High-risk capability
    # -----------------------------------------------------

    high_risk_capability = detect_high_risk_capability(
        description,
        target_customers,
    )

    if high_risk_capability:

        return (
            "Opportunity requires a high-risk "
            "professional capability: "
            f"{high_risk_capability}."
        )

    # -----------------------------------------------------
    # 4. Unsupported founder claims
    # -----------------------------------------------------

    if contains_unsupported_founder_claim(
        why_it_fits,
        founder_profile,
    ):

        return (
            "why_it_fits contains an unsupported claim "
            "about the founder's experience or background."
        )

    # -----------------------------------------------------
    # 5. Required experience
    # -----------------------------------------------------

    if required_experience_copies_founder(
        founder_profile.experience,
        required_experience,
    ):

        return (
            "required_experience appears to copy "
            "the founder's own experience."
        )

    # -----------------------------------------------------
    # 6. Business model
    # -----------------------------------------------------

    if not business_model or not str(
        business_model
    ).strip():

        return "Business model is empty."

    # -----------------------------------------------------
    # Valid
    # -----------------------------------------------------

    return True


# =========================================================
# Validate complete opportunity set
# =========================================================

def validate_opportunity_set(
    opportunities: list[dict],
    founder_profile=None,
) -> bool | str:
    """
    Validate the complete generated opportunity set.

    founder_profile is accepted for compatibility with the
    opportunity router. Set-level validation currently focuses
    on diversity and similarity.
    """

    if len(opportunities) != 5:

        return "Exactly 5 opportunities are required."

    # -----------------------------------------------------
    # 1. Semantic similarity
    # -----------------------------------------------------

    for i in range(len(opportunities)):

        for j in range(i + 1, len(opportunities)):

            similarity = calculate_opportunity_similarity(
                opportunities[i],
                opportunities[j],
            )

            if similarity >= 0.55:

                title_a = opportunities[i].get(
                    "title",
                    "Opportunity A",
                )

                title_b = opportunities[j].get(
                    "title",
                    "Opportunity B",
                )

                return (
                    "Two opportunities are too similar: "
                    f"'{title_a}' and '{title_b}'."
                )

    # -----------------------------------------------------
    # 2. Business-model diversity
    # -----------------------------------------------------

    business_models = [
        normalize_business_model(
            opportunity.get("business_model")
        )
        for opportunity in opportunities
    ]

    model_counts = {}

    for model in business_models:

        model_counts[model] = (
            model_counts.get(model, 0) + 1
        )

    for model, count in model_counts.items():

        if count >= 3:

            return (
                "Too many opportunities use the same "
                f"business model: {model}."
            )

    # -----------------------------------------------------
    # 3. Industry diversity
    # -----------------------------------------------------

    industries = [
        normalize_text(
            opportunity.get("industry")
        )
        for opportunity in opportunities
    ]

    industry_counts = {}

    for industry in industries:

        if industry:

            industry_counts[industry] = (
                industry_counts.get(
                    industry,
                    0,
                ) + 1
            )

    for industry, count in industry_counts.items():

        if count >= 4:

            return (
                "Too many opportunities are concentrated "
                f"in the same industry: {industry}."
            )

    return True