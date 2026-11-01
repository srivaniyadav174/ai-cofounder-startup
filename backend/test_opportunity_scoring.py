from app.database import SessionLocal
from app.models.founder_profile import FounderProfile
from app.models.opportunity import Opportunity
from app.scoring.opportunity_scoring import calculate_opportunity_score


db = SessionLocal()

try:
    profile = (
        db.query(FounderProfile)
        .filter(FounderProfile.user_id == 6)
        .first()
    )

    opportunities = (
        db.query(Opportunity)
        .filter(Opportunity.founder_id == 6)
        .order_by(Opportunity.id)
        .all()
    )

    if profile is None:
        print("Founder profile not found.")
        raise SystemExit

    if not opportunities:
        print("No opportunities found.")
        raise SystemExit

    print("\nFOUNDER PROFILE")
    print("=" * 60)
    print(f"Skills: {profile.skills}")
    print(f"Budget: ₹{profile.budget}")
    print(f"Interests: {profile.interests}")
    print(f"Experience: {profile.experience}")
    print(f"Available time: {profile.available_time}")
    print(f"Business preference: {profile.business_preference}")
    print(f"Risk tolerance: {profile.risk_tolerance}")
    print(f"Short-term goal: {profile.short_term_goal}")
    print(f"Long-term goal: {profile.long_term_goal}")
    print(f"Team status: {profile.team_status}")

    print("\nOPPORTUNITY SCORES")
    print("=" * 60)

    for opportunity in opportunities:

        scores = calculate_opportunity_score(
            profile,
            opportunity
        )

        print(f"\n{opportunity.title}")
        print("-" * 60)

        print(
            f"Skills fit:          {scores['skills_fit']}/20"
        )

        print(
            f"Budget fit:          {scores['budget_fit']}/15"
        )

        print(
            f"Interest fit:        {scores['interest_fit']}/15"
        )

        print(
            f"Experience fit:      {scores['experience_fit']}/10"
        )

        print(
            f"Time fit:            {scores['time_fit']}/10"
        )

        print(
            f"Goal alignment:      {scores['goal_alignment']}/10"
        )

        print(
            f"Risk fit:            {scores['risk_fit']}/10"
        )

        print(
            f"Business model fit:  "
            f"{scores['business_model_fit']}/5"
        )

        print(
            f"Team fit:            {scores['team_fit']}/5"
        )

        print(
            f"OVERALL SCORE:       "
            f"{scores['overall_score']}/100"
        )

finally:
    db.close()