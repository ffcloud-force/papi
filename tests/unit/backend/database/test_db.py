"""
Simple script to test database connection and operations
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database.config import SessionLocal
from backend.database.models import User
from backend.database.init_db import init_db

def test_database():
    # Initialize the database
    init_db()
    
    # Create a session
    db = SessionLocal()
    
    try:
        # Create a test user
        test_user = User(
            name="Test User",
            email="test@example.com",
            password="password123"  # In a real app, hash this password
        )
        
        # Add to session and commit
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f"Created test user with ID: {test_user.id}")
        
        # Query the user
        queried_user = db.query(User).filter(User.email == "test@example.com").first()
        print(f"Queried user: {queried_user.name} ({queried_user.email})")
        
        # Clean up
        db.delete(queried_user)
        db.commit()
        print("Test user deleted")
        
    finally:
        db.close()
    
    print("Database test completed successfully!")

if __name__ == "__main__":
    test_database() 