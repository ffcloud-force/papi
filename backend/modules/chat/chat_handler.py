from backend.services.llm_service import LLMService
from backend.database.persistent.models import ExamQuestionChat, ExamQuestion, QuestionSet
from backend.database.persistent.config import get_db

class ChatHandler:
    def __init__(self):
        self.llm_service = LLMService()
        self.db = next(get_db())

    # DB Operations
    def _get_qanda_for_case_by_topic_for_user(self, case_id: str, general_type: str, specific_type: str, user_id: str) -> list[dict]:
        """
        Get the questions and answers for a case by topic for a user
        """
        topic = f"{general_type}_{specific_type}"
        # should return only one question set
        question_set = self.db.query(QuestionSet).filter(
            QuestionSet.case_id == case_id, 
            QuestionSet.topic == topic, 
            # QuestionSet.user_id == user_id
        ).first()

        questions = []
        for question in question_set.questions:
            questions.append(question)
        # return qanda
        return questions
    
    def _store_chat_for_question(self, question_id: str, chat: list[dict]):
        # check with pydantic model

        
        # create SQLAlchemy model instance
        exam_question_chat = ExamQuestionChat(
            question_id=question_id,
            chat=chat
        )
        self.db.add(exam_question_chat)
        self.db.commit()
        pass

if __name__ == "__main__":
    chat_handler = ChatHandler()
    chat_handler._get_qanda_for_case_by_topic_for_user("99040755c4dca88db3a62ced7d5101a67d856a2528a1a83aca876e56676a805c", "relationships", "attachment_styles", "6b42664c-f83f-4e18-aa84-b204086c399d")