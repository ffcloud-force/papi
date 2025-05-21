import os
from backend.services.database_service import DatabaseService
from backend.api.schemas.user import UserCreate
from backend.handler.llm.prompts.exam_prompts import EXAM_PROMPTS
from backend.database.persistent.models import UserRole


class Seeder:
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def seed_users(self):
        """
        Seed the users table with an admin user and a regular user
        """
        password = os.getenv("ADMIN_PASSWORD")
        if not self.db_service.get_all_users():
            admin = self.db_service.create_user(
                UserCreate(
                    email="admin@papi.com",
                    first_name="Papa",
                    last_name="Smurf",
                    password=password,
                    confirm_password=password,
                    role=UserRole.ADMIN,
                )
            )
            # Print credentials to console for developer
            print("\n" + "=" * 50)
            print(" ADMIN USER CREATED - SAVE THESE CREDENTIALS")
            print("=" * 50)
            print(f" Email: {admin.email}")
            print(f" Password: {password}")
            print("=" * 50 + "\n")

    def seed_prompts(self):
        """
        Seed the prompts table with the exam prompts
        """
        if not self.db_service.get_all_prompts():
            for prompt in EXAM_PROMPTS:
                self.db_service.create_prompt(prompt)
