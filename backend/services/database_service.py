from backend.database.persistent.models import (
    User,
    Case,
    Question,
    QuestionSet,
    CaseDiscussion,
    MessageRole,
)
from backend.api.schemas.chat import (
    CaseDiscussionCreate,
    AnswerDiscussionCreate,
    ChatMessageCreate,
)
from backend.api.schemas.qanda import QuestionRetrieve
from backend.api.schemas.case import CaseCreate
from backend.api.schemas.user import UserCreate
from backend.database.persistent.models import CaseStatus, AnswerDiscussion, Message
from backend.handler.database.database_handler import DatabaseHandler
from backend.utils.password_utils import hash_password
from pydantic import ValidationError
import uuid
from typing import Optional


class DatabaseService:
    def __init__(self, db_handler: DatabaseHandler):
        self.db_handler = db_handler

    # User-specific operations
    def create_user(self, user_data: UserCreate):
        try:
            validated_user_data = UserCreate.model_validate(user_data)
            # Check if user exists
            existing_user = self.db_handler._get_user_by_email(
                validated_user_data.email
            )
            if existing_user:
                raise ValueError("User with this email already exists")

            # Hash the password
            hashed_password = hash_password(validated_user_data.password)
            # Create new user
            new_user = User(
                id=str(uuid.uuid4()),
                email=validated_user_data.email,
                first_name=validated_user_data.first_name,
                last_name=validated_user_data.last_name,
                password_hash=hashed_password,
            )

            return self.db_handler._create_user(new_user)
        except ValidationError as e:
            print(f"User data validation failed: {e}")
            raise ValueError("Invalid user data") from e

    def get_user_by_id(self, user_id):
        # TODO: Add validation
        return self.db_handler._get_user_by_id(user_id)

    def get_user_by_email(self, email):
        # TODO: Add validation
        return self.db_handler._get_user_by_email(email)

    def get_all_users(self):
        # TODO: Add validation
        return self.db_handler._get_all_users()

    def update_user_last_login(self, user_id):
        # TODO: Add validation
        return self.db_handler._update_user_last_login(user_id)

    def update_user(self, user_id, update_data):
        # TODO: Add validation
        return self.db_handler._update_user(user_id, update_data)

    def delete_user(self, user_id):
        # TODO: Add validation
        return self.db_handler._delete_user(user_id)

    # Case-specific operations
    def create_case(
        self, filename, user_id, s3_key, case_id, case_content, case_number
    ):
        file_type = filename.split(".")[-1].lower() if "." in filename else None

        try:
            # Create and validate with Pydantic
            case_model = CaseCreate(
                filename=filename,
                file_type=file_type,
                file_size=len(case_content),
                case_content=case_content,
                case_number=case_number,
                user_id=user_id,
            )

            # Create SQLAlchemy model instance
            case = Case(
                id=case_id,
                filename=case_model.filename,
                storage_path=s3_key,
                content_text=case_model.case_content,
                file_type=case_model.file_type,
                file_size=case_model.file_size,
                status=CaseStatus.UPLOADED,
                case_number=case_model.case_number,
                case_metadata=case_model.case_metadata,
                user_id=case_model.user_id,
            )

            try:
                self.db_handler._create_case(case)
            except Exception as e:
                raise e
            return case

        except ValidationError as e:
            print(f"Case data validation failed: {e}")
            # You can log, handle, or re-raise as needed
            raise ValueError("Invalid case data") from e

    def get_all_cases_for_user(self, user_id):
        # TODO: Add validation and error handling
        return self.db_handler._get_all_cases_for_user(user_id)

    def get_case_by_id(self, case_id):
        # TODO: Add validation and error handling
        return self.db_handler._get_case_by_id(case_id)

    def update_case_status(self, case_id, status):
        # TODO: Add validation and error handling
        return self.db_handler._update_case_status(case_id, status)

    def delete_case_from_db(self, case_id):
        # TODO: Add validation and error handling
        return self.db_handler._delete_case(case_id)

    # Question-specific operations
    def create_questions_and_set(
        self, questions: dict[str, list[Question]], user_id: int, case_id: int
    ) -> tuple[QuestionSet, list[Question]]:
        """
        Create question sets for all topics in a single transaction.
        Each topic gets its own QuestionSet.

        Args:
            questions: Dictionary mapping topics to lists of Question objects
            user_id: ID of the user creating the questions
            case_id: ID of the case these questions refer to
        """
        try:
            # question_sets = {}
            # Begin transaction
            for topic, question_list in questions.items():
                # Create a QuestionSet for this topic
                question_set = QuestionSet(case_id=case_id, topic=topic)

            question_set, questions = (
                self.db_handler._create_question_set_and_questions(
                    question_set, question_list
                )
            )
            return question_set, questions

        except Exception as e:
            print(f"Error creating question sets: {str(e)}")
            raise

    def get_questions_by_topic_for_user(
        self, case_id: str, general_type: str, specific_type: str, user_id: str
    ) -> list[dict]:
        """
        Get questions by topic for a user

        Args:
            case_id: ID of the case
            general_type: General type of the questions
            specific_type: Specific type of the questions
            user_id: ID of the user

        Returns:
            List of questions
        """
        topic = f"{general_type}_{specific_type}"
        question_set = self.db_handler.get_question_set_by_topic_for_user(
            case_id, topic, user_id
        )

        validated_questions = []
        for question in question_set.questions:
            try:
                validated_question = QuestionRetrieve(
                    id=question.id,
                    question=question.question,
                    context=question.context,
                    difficulty=question.difficulty,
                    keywords=question.keywords,
                    general_type=question.general_type,
                    specific_type=question.specific_type,
                    answer=question.answer,
                )
                validated_questions.append(validated_question)
            except Exception as e:
                print(f"Error validating question: {str(e)}")
                continue
        return validated_questions

    def get_question_by_id(self, question_id: int) -> Question:
        """
        Get a question by its ID

        Args:
            question_id: ID of the question

        Returns:
            Question object
        """
        question = self.db_handler._get_question_by_id(question_id)
        if not question:
            raise ValueError(f"Question with ID {question_id} not found")
        return question

    # Chat-specific operations
    def create_case_discussion(
        self, case_id: str, user_id: str, topic: Optional[str] = None
    ) -> CaseDiscussion:
        validated_case_discussion_data = CaseDiscussionCreate.model_validate(
            {"case_id": case_id, "user_id": user_id}
        )

        case_discussion = CaseDiscussion(
            case_id=validated_case_discussion_data.case_id,
            user_id=validated_case_discussion_data.user_id,
        )
        return self.db_handler._create_case_discussion(case_discussion)

    def get_case_discussions(self, case_id: str, user_id: str) -> list[CaseDiscussion]:
        """
        Get case discussions for a specific case and user

        Args:
            case_id: ID of the case
            user_id: ID of the user

        Returns:
            List of CaseDiscussion objects with eager-loaded answer discussions
        """
        return self.db_handler._get_case_discussions(case_id, user_id)

    async def get_unanswered_questions_by_topic(
        self, case_id: str, topic: str
    ) -> list[Question]:
        return self.db_handler._get_unanswered_questions_by_topic(case_id, topic)

    def get_all_unanswered_questions(self, case_id: str) -> list[Question]:
        return self.db_handler._get_all_unanswered_questions(case_id)

    def create_answer_discussion(
        self, case_discussion_id: int, selected_question_id: int
    ) -> AnswerDiscussion:
        validated_answer_discussion_data = AnswerDiscussionCreate.model_validate(
            {
                "case_discussion_id": case_discussion_id,
                "question_id": selected_question_id,
            }
        )

        answer_discussion = AnswerDiscussion(
            case_discussion_id=validated_answer_discussion_data.case_discussion_id,
            question_id=validated_answer_discussion_data.question_id,
        )

        return self.db_handler._create_answer_discussion(answer_discussion)

    def get_answer_discussion_by_id(
        self, answer_discussion_id: int
    ) -> AnswerDiscussion:
        """
        Get an answer discussion by its ID

        Args:
            answer_discussion_id: ID of the answer discussion

        Returns:
            AnswerDiscussion object
        """
        answer_discussion = self.db_handler._get_answer_discussion_by_id(
            answer_discussion_id
        )
        if not answer_discussion:
            raise ValueError(
                f"Answer discussion with ID {answer_discussion_id} not found"
            )
        return answer_discussion

    def get_messages_by_answer_discussion_id(
        self, answer_discussion_id: int
    ) -> list[Message]:
        """
        Get all messages for a specific answer discussion

        Args:
            answer_discussion_id: ID of the answer discussion

        Returns:
            List of Message objects
        """
        messages = self.db_handler._get_messages_by_answer_discussion_id(
            answer_discussion_id
        )
        return messages

    def create_chat_message(
        self, role: MessageRole, content: str, answer_discussion_id: int
    ) -> Message:
        validated_chat_message_data = ChatMessageCreate.model_validate(
            {
                "role": role,
                "content": content,
                "answer_discussion_id": answer_discussion_id,
            }
        )

        chat_message = Message(
            role=validated_chat_message_data.role,
            content=validated_chat_message_data.content,
            answer_discussion_id=validated_chat_message_data.answer_discussion_id,
        )

        return self.db_handler._create_message(chat_message)
