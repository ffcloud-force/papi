from backend.services.llm_service import LLMService
from backend.services.database_service import DatabaseService

class ChatService:
    def __init__(self):
        self.llm_service = LLMService()
        self.db_service = DatabaseService()
