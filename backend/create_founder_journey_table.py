from app.database import engine
from app.models.founder_journey import FounderJourney


print("Creating founder_journeys table...")

FounderJourney.__table__.create(
    bind=engine,
    checkfirst=True
)

print("founder_journeys table created successfully.")