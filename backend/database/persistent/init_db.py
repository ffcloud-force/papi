"""
Script to initialize the database
"""

from backend.database.persistent.config import engine
from backend.database.persistent.models import Base
from backend.database.persistent.models import (
    User,
    Case,
    QuestionSet,
    Question,
    CaseDiscussion,
    AnswerDiscussion,
    Message,
    UserAnswer,
)


def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    print("Creating database tables...")
    init_db()
    print("Database initialized successfully.")
