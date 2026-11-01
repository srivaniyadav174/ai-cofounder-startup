
import json
import re
import time

import ollama


OLLAMA_MODEL = "llama3.2:3b"


# ============================================================
# JSON EXTRACTION
# ============================================================

def extract_json(text: str) -> dict:
    if not text:
        raise ValueError(
            "AI returned an empty response"
        )

    cleaned = text.strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned
    )

    try:
        return json.loads(cleaned)

    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(
            "AI response did not contain valid JSON"
        )

    try:
        return json.loads(
            cleaned[start:end + 1]
        )

    except json.JSONDecodeError as exc:
        raise ValueError(
            "AI returned malformed JSON"
        ) from exc


# ============================================================
# VALIDATE MVP PLAN
# ============================================================

def validate_mvp_plan(data: dict) -> dict:

    required_fields = [
        "title",
        "objective",
        "problem_to_solve",
        "target_customer",
        "core_value_proposition",
        "scope",
        "success_metrics",
        "estimated_duration_days",
        "milestones"
    ]

    for field in required_fields:

        if field not in data:
            raise ValueError(
                f"MVP plan missing required field: {field}"
            )

    if not isinstance(
        data["milestones"],
        list
    ):
        raise ValueError(
            "milestones must be a list"
        )

    if len(data["milestones"]) < 2:
        raise ValueError(
            "MVP plan must contain at least 2 milestones"
        )

    if len(data["milestones"]) > 8:
        raise ValueError(
            "MVP plan cannot contain more than 8 milestones"
        )

    try:

        duration = int(
            data["estimated_duration_days"]
        )

    except (TypeError, ValueError) as exc:

        raise ValueError(
            "estimated_duration_days must be an integer"
        ) from exc

    if duration < 1 or duration > 180:
        raise ValueError(
            "estimated_duration_days must be between 1 and 180"
        )

    for milestone_number, milestone in enumerate(
        data["milestones"],
        start=1
    ):

        if not isinstance(
            milestone,
            dict
        ):
            raise ValueError(
                f"Milestone {milestone_number} "
                "must be an object"
            )

        required_milestone_fields = [
            "title",
            "description",
            "order_index",
            "target_days",
            "tasks"
        ]

        for field in required_milestone_fields:

            if field not in milestone:
                raise ValueError(
                    f"Milestone {milestone_number} "
                    f"missing required field: {field}"
                )

        if not isinstance(
            milestone["tasks"],
            list
        ):
            raise ValueError(
                f"Milestone {milestone_number} "
                "tasks must be a list"
            )

        if len(milestone["tasks"]) == 0:
            raise ValueError(
                f"Milestone {milestone_number} "
                "must contain at least one task"
            )

        try:

            order_index = int(
                milestone["order_index"]
            )

            target_days = int(
                milestone["target_days"]
            )

        except (TypeError, ValueError) as exc:

            raise ValueError(
                f"Milestone {milestone_number} "
                "numeric fields must be integers"
            ) from exc

        if order_index < 1:
            raise ValueError(
                f"Milestone {milestone_number} "
                "has invalid order_index"
            )

        if target_days < 1:
            raise ValueError(
                f"Milestone {milestone_number} "
                "has invalid target_days"
            )

        for task_number, task in enumerate(
            milestone["tasks"],
            start=1
        ):

            if not isinstance(
                task,
                dict
            ):
                raise ValueError(
                    f"Task {task_number} in milestone "
                    f"{milestone_number} must be an object"
                )

            required_task_fields = [
                "title",
                "description",
                "priority"
            ]

            for field in required_task_fields:

                if field not in task:
                    raise ValueError(
                        f"Task {task_number} in milestone "
                        f"{milestone_number} missing {field}"
                    )

            try:

                priority = int(
                    task["priority"]
                )

            except (TypeError, ValueError) as exc:

                raise ValueError(
                    f"Task {task_number} priority "
                    "must be an integer"
                ) from exc

            if priority < 1 or priority > 5:
                raise ValueError(
                    f"Task {task_number} priority "
                    "must be between 1 and 5"
                )

    return data


# ============================================================
# AI MVP GENERATOR
# ============================================================

def generate_mvp_plan(
    startup,
    decision,
    experiments
) -> dict:

    experiment_evidence = []

    for experiment in experiments:

        experiment_evidence.append(
            {
                "title": experiment.title,
                "hypothesis": experiment.hypothesis,
                "experiment_type": experiment.experiment_type,
                "description": experiment.description,
                "success_criteria": experiment.success_criteria,
                "result": experiment.result,
                "learning": experiment.learning,
                "next_action": experiment.next_action
            }
        )

    prompt = f"""
You are a startup product strategist.

You are generating a practical MVP execution plan
for a startup decision-support platform.

This is NOT a chatbot response.

Use only the evidence provided below.

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
VALIDATION DECISION
============================================================

Decision:
{decision.decision}

Confidence:
{decision.confidence_score}

Evidence Summary:
{decision.evidence_summary}

Strengths:
{decision.strengths}

Weaknesses:
{decision.weaknesses}

Key Learnings:
{decision.key_learnings}

Recommendation:
{decision.recommendation}

MVP Scope:
{decision.mvp_scope}

Next Actions:
{decision.next_actions}

============================================================
VALIDATION EXPERIMENTS
============================================================

{json.dumps(
    experiment_evidence,
    indent=2,
    ensure_ascii=False
)}

============================================================
MVP REQUIREMENTS
============================================================

Create the smallest useful MVP.

The MVP must:

1. Solve the validated customer problem.
2. Focus on the core value proposition.
3. Avoid unnecessary features.
4. Use validation evidence.
5. Respect the validation decision.
6. Convert the MVP into milestones.
7. Convert milestones into concrete tasks.
8. Prioritize customer value.
9. Avoid unsupported claims.
10. Never invent customers, revenue, statistics,
   partnerships, or validation results.
11. Be realistic for a small startup team.
12. Clearly define what is out of scope.

Create 3 to 6 milestones.

Each milestone must contain 2 to 6 concrete tasks.

============================================================
OUTPUT
============================================================

Return ONLY valid JSON.

Use exactly this structure:

{{
  "title": "MVP plan title",
  "objective": "MVP objective",
  "problem_to_solve": "Customer problem",
  "target_customer": "Primary customer",
  "core_value_proposition": "Core value proposition",
  "scope": "Features and work included",
  "out_of_scope": "Features intentionally excluded",
  "success_metrics": "How MVP success will be measured",
  "estimated_duration_days": 30,
  "status": "PLANNED",
  "milestones": [
    {{
      "title": "Milestone title",
      "description": "Milestone description",
      "order_index": 1,
      "status": "NOT_STARTED",
      "target_days": 5,
      "tasks": [
        {{
          "title": "Task title",
          "description": "Concrete task description",
          "priority": 1,
          "estimated_hours": 4,
          "status": "TODO",
          "due_days": 2
        }}
      ]
    }}
  ]
}}

Do not return markdown.

Do not return explanations.

Return JSON only.
"""

    try:

        generation_started = time.perf_counter()

        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "num_predict": 800
            }
        )

        generation_seconds = (
            time.perf_counter() - generation_started
        )

        print(
            f"[MVP GENERATOR] Ollama generation took "
            f"{generation_seconds:.2f} seconds"
        )

    except Exception as exc:

        raise RuntimeError(
            f"Ollama MVP generation failed: {exc}"
        ) from exc

    content = response["message"]["content"]

    data = extract_json(content)

    return validate_mvp_plan(data)
