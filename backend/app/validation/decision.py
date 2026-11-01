import json
import re

from fastapi import HTTPException, status
from ollama import chat
from sqlalchemy.orm import Session

from app.models.startup import Startup
from app.models.validation_experiment import ValidationExperiment
from app.models.validation_decision import ValidationDecision


OLLAMA_MODEL = "llama3:latest"


VALID_DECISIONS = {
    "PROCEED_TO_MVP",
    "CONTINUE_VALIDATION",
    "PIVOT",
    "STOP",
}


# ============================================================
# JSON EXTRACTION
# ============================================================

def extract_json(text: str):
    """
    Extract JSON from an Ollama response.

    Handles:
    - plain JSON
    - markdown JSON code blocks
    - explanatory text surrounding JSON
    """

    if not text:
        raise ValueError(
            "AI returned an empty response."
        )

    cleaned = text.strip()

    # Remove markdown code fences.
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

    # Try the complete response first.
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Find an embedded JSON object.
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(
            "AI response does not contain valid JSON."
        )

    return json.loads(
        cleaned[start:end + 1]
    )


# ============================================================
# VALIDATION HELPERS
# ============================================================

def normalize_decision(value: str) -> str:
    """
    Normalize AI decision labels.
    """

    if not value:
        raise ValueError(
            "AI did not provide a decision."
        )

    normalized = value.strip().upper()

    aliases = {
        "PROCEED": "PROCEED_TO_MVP",
        "BUILD": "PROCEED_TO_MVP",
        "BUILD_MVP": "PROCEED_TO_MVP",
        "PROCEED TO MVP": "PROCEED_TO_MVP",

        "CONTINUE": "CONTINUE_VALIDATION",
        "VALIDATE": "CONTINUE_VALIDATION",
        "CONTINUE VALIDATION": "CONTINUE_VALIDATION",

        "PIVOT": "PIVOT",

        "STOP": "STOP",
        "ABANDON": "STOP",
    }

    normalized = aliases.get(
        normalized,
        normalized,
    )

    if normalized not in VALID_DECISIONS:
        raise ValueError(
            f"Invalid AI decision: {normalized}"
        )

    return normalized


def validate_decision_result(data: dict):
    """
    Validate the structured AI decision.
    """

    if not isinstance(data, dict):
        raise ValueError(
            "AI response must be a JSON object."
        )

    required_fields = {
        "decision",
        "confidence_score",
        "evidence_summary",
        "strengths",
        "weaknesses",
        "key_learnings",
        "recommendation",
        "mvp_scope",
        "next_actions",
    }

    missing = required_fields - data.keys()

    if missing:
        raise ValueError(
            "AI response is missing fields: "
            + ", ".join(sorted(missing))
        )

    decision = normalize_decision(
        data["decision"]
    )

    try:
        confidence_score = int(
            data["confidence_score"]
        )
    except (TypeError, ValueError):
        confidence_score = 50

    confidence_score = max(
        1,
        min(confidence_score, 100),
    )

    def normalize_text(value, default=""):
        if value is None:
            return default

        if isinstance(value, list):
            return "\n".join(
                f"- {str(item).strip()}"
                for item in value
                if str(item).strip()
            )

        return str(value).strip()

    result = {
        "decision": decision,

        "confidence_score": confidence_score,

        "evidence_summary": normalize_text(
            data["evidence_summary"]
        )[:10000],

        "strengths": normalize_text(
            data["strengths"]
        )[:10000],

        "weaknesses": normalize_text(
            data["weaknesses"]
        )[:10000],

        "key_learnings": normalize_text(
            data["key_learnings"]
        )[:10000],

        "recommendation": normalize_text(
            data["recommendation"]
        )[:10000],

        "mvp_scope": normalize_text(
            data["mvp_scope"]
        )[:10000],

        "next_actions": normalize_text(
            data["next_actions"]
        )[:10000],
    }

    return result


# ============================================================
# BUILD EVIDENCE CONTEXT
# ============================================================

def build_experiment_evidence(
    experiments: list[ValidationExperiment],
) -> str:
    """
    Convert persisted experiment records into a structured
    evidence package for the AI.
    """

    evidence_blocks = []

    for index, experiment in enumerate(
        experiments,
        start=1,
    ):

        evidence_blocks.append(
            f"""
EXPERIMENT {index}

Title:
{experiment.title}

Type:
{experiment.experiment_type}

Hypothesis:
{experiment.hypothesis}

Description:
{experiment.description}

Success Criteria:
{experiment.success_criteria}

Status:
{experiment.status}

Result:
{experiment.result or "No result recorded."}

Learning:
{experiment.learning or "No learning recorded."}

Next Action:
{experiment.next_action or "No next action recorded."}

Priority:
{experiment.priority}
"""
        )

    return "\n".join(evidence_blocks)


# ============================================================
# AI DECISION GENERATOR
# ============================================================

def generate_validation_decision(
    startup: Startup,
    experiments: list[ValidationExperiment],
):
    """
    Analyze completed validation evidence and generate
    a structured startup validation decision.
    """

    evidence = build_experiment_evidence(
        experiments
    )

    prompt = f"""
You are a startup validation decision engine.

You are part of an AI-powered startup intelligence
and decision-support platform.

You are NOT a chatbot.

Your responsibility is to analyze real validation
evidence and recommend the next business action.

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

Target Market:
{startup.target_market}

Business Model:
{startup.business_model}

============================================================
VALIDATION EVIDENCE
============================================================

{evidence}

============================================================
DECISION FRAMEWORK
============================================================

Choose exactly ONE decision:

1. PROCEED_TO_MVP

Use this when the evidence provides meaningful support
for the core problem and customer demand, and the
remaining uncertainty is reasonable to address through
a focused MVP.

2. CONTINUE_VALIDATION

Use this when the idea may be promising but there is
not enough evidence yet to justify building an MVP.

3. PIVOT

Use this when the experiments reveal that the original
assumption, customer segment, problem, pricing model,
or solution direction is substantially wrong, but the
evidence suggests another direction may be worth testing.

4. STOP

Use this when the evidence strongly suggests that the
problem is weak, customers do not care, the economics
are fundamentally unattractive, or the idea is not
worth further validation.

============================================================
IMPORTANT RULES
============================================================

- Do NOT invent evidence.
- Do NOT invent customer numbers.
- Do NOT invent revenue.
- Do NOT assume an experiment succeeded if no result
  was recorded.
- Distinguish between evidence and assumptions.
- Completed experiments without results are NOT strong
  evidence.
- Customer behavior is stronger evidence than opinions.
- Willingness to pay is stronger evidence than saying
  an idea sounds useful.
- Do not recommend building a large product based only
  on interviews.
- Prefer a narrow MVP.
- If evidence is insufficient, choose
  CONTINUE_VALIDATION rather than guessing.
- Be conservative about PROCEED_TO_MVP.
- Confidence should reflect the quality and quantity
  of actual evidence.

============================================================
OUTPUT
============================================================

Return ONLY valid JSON.

Required format:

{{
    "decision": "PROCEED_TO_MVP",
    "confidence_score": 82,
    "evidence_summary": "...",
    "strengths": [
        "...",
        "..."
    ],
    "weaknesses": [
        "...",
        "..."
    ],
    "key_learnings": [
        "...",
        "..."
    ],
    "recommendation": "...",
    "mvp_scope": [
        "...",
        "..."
    ],
    "next_actions": [
        "...",
        "..."
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
                "AI validation decision service is "
                "unavailable. Make sure Ollama is running."
            ),
        ) from exc

    try:

        content = response["message"]["content"]

        parsed = extract_json(content)

        return validate_decision_result(
            parsed
        )

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "The AI generated an invalid validation "
                "decision."
            ),
        ) from exc


# ============================================================
# SAVE VALIDATION DECISION
# ============================================================

def save_validation_decision(
    db: Session,
    founder_id: int,
    startup_id: int,
    decision_data: dict,
):
    """
    Persist the AI decision in PostgreSQL.
    """

    # Remove any previous decision for this startup.
    db.query(ValidationDecision).filter(
        ValidationDecision.founder_id == founder_id,
        ValidationDecision.startup_id == startup_id,
    ).delete(
        synchronize_session=False
    )

    decision = ValidationDecision(
        founder_id=founder_id,
        startup_id=startup_id,

        decision=decision_data["decision"],

        confidence_score=(
            decision_data["confidence_score"]
        ),

        evidence_summary=(
            decision_data["evidence_summary"]
        ),

        strengths=(
            decision_data["strengths"]
        ),

        weaknesses=(
            decision_data["weaknesses"]
        ),

        key_learnings=(
            decision_data["key_learnings"]
        ),

        recommendation=(
            decision_data["recommendation"]
        ),

        mvp_scope=(
            decision_data["mvp_scope"]
        ),

        next_actions=(
            decision_data["next_actions"]
        ),
    )

    db.add(decision)

    db.commit()
    db.refresh(decision)

    return decision