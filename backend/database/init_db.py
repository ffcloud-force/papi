"""
Script to initialize the database
"""

from backend.database.config import engine, Base
from backend.database.models import User, Document

def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
if __name__ == "__main__":
    print("Creating database tables...")
    init_db()
    print("Database initialized successfully.") 