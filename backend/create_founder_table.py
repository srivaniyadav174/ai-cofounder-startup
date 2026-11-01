from app.database import engine, Base

# Import all models so SQLAlchemy knows about them
from app.models.user import User
from app.models.startup import Startup
from app.models.founder_profile import FounderProfile


print("Creating founder_profiles table...")

FounderProfile.__table__.create(
    bind=engine,
    checkfirst=True
)

print("founder_profiles table created successfully.")