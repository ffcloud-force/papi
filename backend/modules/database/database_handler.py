from backend.database.persistent.config import get_db
from backend.database.persistent.models import QuestionSet, ExamQuestion, User, Case
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError

class DatabaseHandler:
    def __init__(self):
        self.db = next(get_db())

    # User-specific operations
    def _create_user(self, user_data):
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        return user

    def _get_user_by_id(self, user_id):
        return self.db.query(User).filter(User.id == user_id).first()

    # Case-specific operations
    def _create_case(self, case_data):
        case = Case(**case_data)
        self.db.add(case)
        self.db.commit()
        return case

    def create_question_set(self, question_set: QuestionSet) -> QuestionSet:
        try:
            self.db.add(question_set)
            self.db.flush()
            self.db.commit()
            return question_set
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def create_question(self, question: ExamQuestion) -> ExamQuestion:
        try:
            self.db.add(question)
            self.db.flush()
            self.db.commit()
            return question
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    # Question-set specific operations
    def _get_question_set_by_topic_for_user(self, case_id: str, topic: str, user_id: str) -> QuestionSet | None:
        question_set = self.db.query(QuestionSet)\
            .options(joinedload(QuestionSet.questions))\
            .filter(
                QuestionSet.case_id == case_id,
                QuestionSet.topic == topic,
                QuestionSet.user_id == user_id
            )\
            .first()
        if question_set is None:
            return None
        return question_set
