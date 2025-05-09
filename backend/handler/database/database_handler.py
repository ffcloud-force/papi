from backend.database.persistent.models import (
    QuestionSet,
    Question,
    User,
    Case,
    CaseStatus,
    CaseDiscussion,
    AnswerDiscussion,
    Message
)
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from sqlalchemy.orm import Session


class DatabaseHandler:
    def __init__(self, db: Session):
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
        self, question_set: QuestionSet, questions: list[Question]
    ) -> tuple[QuestionSet, list[Question]]:
        try:
            self.db.add(question_set)
            self.db.flush()
            for question in questions:
                question.question_set_id = question_set.id
                self.db.add(question)
            self.db.commit()
            return question_set, questions
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def _create_case_discussion(
        self, case_discussion: CaseDiscussion
    ) -> CaseDiscussion:
        try:
            self.db.add(case_discussion)
            self.db.commit()
            return case_discussion
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def _create_answer_discussion(
        self, answer_discussion: AnswerDiscussion
    ) -> AnswerDiscussion:
        try:
            self.db.add(answer_discussion)
            self.db.commit()
            return answer_discussion
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
        
    def _create_message(
            self, message: Message
    ) -> Message:
        try:
            self.db.add(message)
            self.db.commit()
            return message
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e


    # RETRIEVE
    def _get_user_by_id(self, user_id) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def _get_user_by_email(self, email) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def _get_all_users(self) -> list[User] | None:
        return self.db.query(User).all()

    def _get_case_by_id(self, case_id) -> Case | None:
        return self.db.query(Case).filter(Case.id == case_id).first()
        
    def _get_question_by_id(self, question_id: int) -> Question | None:
        """
        Get a question by its ID
        
        Args:
            question_id: ID of the question
            
        Returns:
            Question object or None if not found
        """
        return self.db.query(Question).filter(Question.id == question_id).first()
        
    def _get_answer_discussion_by_id(self, answer_discussion_id: int) -> AnswerDiscussion | None:
        """
        Get an answer discussion by its ID
        
        Args:
            answer_discussion_id: ID of the answer discussion
            
        Returns:
            AnswerDiscussion object or None if not found
        """
        return (
            self.db.query(AnswerDiscussion)
            .options(joinedload(AnswerDiscussion.question))
            .filter(AnswerDiscussion.id == answer_discussion_id)
            .first()
        )
        
    def _get_messages_by_answer_discussion_id(self, answer_discussion_id: int) -> list[Message]:
        """
        Get all messages for a specific answer discussion, ordered by creation time
        
        Args:
            answer_discussion_id: ID of the answer discussion
            
        Returns:
            List of Message objects
        """
        return (
            self.db.query(Message)
            .filter(Message.answer_discussion_id == answer_discussion_id)
            .order_by(Message.created_at)
            .all()
        )

    def _get_all_cases_for_user(self, user_id) -> list[Case] | None:
        return self.db.query(Case).filter(Case.user_id == user_id).all()

    def _get_question_set_by_topic_and_user(
        self, case_id: str, topic: str, user_id: str
    ) -> QuestionSet | None:
        question_set = (
            self.db.query(QuestionSet)
            .options(joinedload(QuestionSet.questions))
            .filter(
                QuestionSet.case_id == case_id,
                QuestionSet.topic == topic,
                QuestionSet.user_id == user_id,
            )
            .first()
        )
        if question_set is None:
            return None
        return question_set

    def _get_unanswered_questions_by_topic(
        self, case_id: str, topic: str
    ) -> list[Question] | None:
        questions = (
            self.db.query(Question)
            .join(QuestionSet)
            .filter(
                QuestionSet.case_id == case_id,
                QuestionSet.topic == topic,
            )
            .all()
        )
        if questions is None:
            return None
        return questions

    async def _get_all_unanswered_questions(
        self, case_id: str
    ) -> list[Question] | None:
        questions = (
            self.db.query(Question)
            .join(QuestionSet)
            .filter(
                QuestionSet.case_id == case_id,
            )
            .all()
        )
        return questions

    def _get_case_discussions(self, case_id: str, user_id: str) -> list[CaseDiscussion]:
        """
        Get all case discussions for a specific case and user, with eager loading of answer discussions
        
        Args:
            case_id: ID of the case
            user_id: ID of the user
            
        Returns:
            List of CaseDiscussion objects with answer_discussions eager-loaded
        """
        return (
            self.db.query(CaseDiscussion)
            .options(joinedload(CaseDiscussion.answer_discussions))
            .filter(
                CaseDiscussion.case_id == case_id,
                CaseDiscussion.user_id == user_id
            )
            .order_by(CaseDiscussion.last_message_at.desc())
            .all()
        )

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
