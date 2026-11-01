from app.database import engine
from app.models.opportunity import Opportunity


print("Creating opportunities table...")

Opportunity.__table__.create(
    bind=engine,
    checkfirst=True
)

print("opportunities table created successfully.")