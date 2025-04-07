from backend.database.persistent.models import QuestionSet, Question, User, Case, CaseStatus
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from sqlalchemy.orm import Session

class DatabaseHandler:
    def __init__(
        self,
        db: Session
    ):
        self.db = db

    # CREATE
    def _create_user(self, user_data):
        try:
            self.db.add(user_data)
            self.db.commit()
            return user_data
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def _create_case(self, case_data):
        try:
            self.db.add(case_data)
            self.db.commit()
            return case_data
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def _create_question_set(self, question_set: QuestionSet) -> QuestionSet:
        try:
            self.db.add(question_set)
            self.db.commit()
            return question_set
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def _create_question(self, question: Question) -> Question:
        try:
            self.db.add(question)
            self.db.commit()
            return question
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def _create_question_set_and_questions(
            self, 
            question_set: QuestionSet, 
            questions: list[Question]
        ) -> tuple[QuestionSet, list[Question]]:
        try:
            self.db.add(question_set)
            for question in questions:
                question.question_set_id = question_set.id
                self.db.add(question)
            self.db.commit()
            return question_set, questions
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    # def _create_chat_session

    # RETRIEVE
    def _get_user_by_id(self, user_id) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def _get_user_by_email(self, email) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def _get_all_users(self) -> list[User] | None:
        return self.db.query(User).all()

    def _get_case_by_id(self, case_id) -> Case | None:
        return self.db.query(Case).filter(Case.id == case_id).first()

    def _get_all_cases_for_user(self, user_id) -> list[Case] | None:
        return self.db.query(Case).filter(Case.user_id == user_id).all()

    def _get_question_set_by_topic_and_user(self, case_id: str, topic: str, user_id: str) -> QuestionSet | None:
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

    # UPDATE
    def _update_user(self, user_id: str, update_data: dict) -> User | None:
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            self.db.commit()
            return user
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def _update_user_last_login(self, user_id: str) -> User | None:
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            user.last_login = datetime.now()
            self.db.commit()
            return user
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def _update_case(self, case_id: str, update_data: dict) -> Case | None:
        """Generic update function for any case fields"""
        try:
            case = self.db.query(Case).filter(Case.id == case_id).first()
            if not case:
                return None
            
            for key, value in update_data.items():
                if hasattr(case, key):
                    setattr(case, key, value)
                
            self.db.commit()
            return case
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def _update_case_status(self, case_id: str, status: CaseStatus) -> Case | None:
        """Specific function for updating status with type safety"""
        try:
            case = self.db.query(Case).filter(Case.id == case_id).first()
            if not case:
                return None
            
            case.status = status  # Type checking happens here
            self.db.commit()
            return case
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    # DELETE
    def _delete_case(self, case_id: str) -> None:
        case = self.db.query(Case).filter(Case.id == case_id).first()
        if case:
            self.db.delete(case)
            self.db.commit()
        else:
            raise ValueError(f"Case with id {case_id} not found")

    def _delete_user(self, user_id: str) -> None:
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            self.db.delete(user)
            self.db.commit()
        else:
            raise ValueError(f"User with id {user_id} not found")