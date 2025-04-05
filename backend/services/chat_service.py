from backend.services.llm_service import LLMService
from backend.services.database_service import DatabaseService

"""
ChatService
-user clicks on the chat tab
-user selects a case
-check if there is an existing chat session for the user for that case (first redis than database)
-if there is, open the existing chat session
-if there is not, open new chat session
-user can select topic or select all (all is default)
-check if there is an unanswered question for that topic (if all is selected go through all topics in order of topic list)
...
"""

class ChatService:
    def __init__(self, llm_service: LLMService, db_service: DatabaseService):
        self.llm_service = llm_service
        self.db_service = db_service

    def start_chat_session_for_topic(self, user_id: str, case_id: str, topic: str):
        """start a new chat session for a user"""
        self.db_service.create_chat_session(user_id, case_id, topic)