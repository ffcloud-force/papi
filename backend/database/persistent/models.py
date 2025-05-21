from sqlalchemy import (
    String,
    Integer,
    DateTime,
    ForeignKey,
    Text,
    Boolean,
    CheckConstraint,
    Enum as SQLAlchemyEnum,
)
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy.types import TypeDecorator, JSON
from datetime import datetime
from enum import Enum
import json
import uuid


class Base(DeclarativeBase):
    pass


# For SQLite compatibility with JSON
class JSONType(TypeDecorator):
    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"

    def is_admin(self):
        return self == UserRole.ADMIN

    def can_access_resource(self, resource_owner_id: str, current_user_id: str):
        return self == UserRole.ADMIN or resource_owner_id == current_user_id


# User model
class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(254), unique=True, nullable=False, index=True
    )
    email_verified: Mapped[bool] = mapped_column(
        default=True
    )  # @TODO: set to false once email verification is implemented
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLAlchemyEnum(UserRole, name="user_role_enum", create_type=False),
        default=UserRole.USER,
        nullable=False,
    )
    registration_date: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now()
    )
    last_login_date: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now()
    )

    # Relationships
    cases: Mapped[list["Case"]] = relationship(
        "Case", back_populates="user", cascade="all, delete-orphan"
    )


class CaseStatus(Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Case(Base):
    """
    Cases are the documents that the user uploads.
    """

    __tablename__ = "cases"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(
        String(255), nullable=False
    )  # original filename
    storage_path: Mapped[str] = mapped_column(
        String(255), nullable=False
    )  # path to the document in the cloud storage
    upload_date: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now()
    )
    file_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # type of the file (pdf, docx, etc.)
    file_size: Mapped[int] = mapped_column(
        Integer, CheckConstraint("file_size > 0")
    )  # size of the file in bytes
    status: Mapped[CaseStatus] = mapped_column(
        SQLAlchemyEnum(CaseStatus, name="case_status_enum", create_type=False),
        default=CaseStatus.UPLOADED,
        nullable=False,
    )  # status of the document (uploaded, processed, etc.)
    case_number: Mapped[int] = mapped_column(Integer)  # 1 or 2
    case_metadata: Mapped[dict] = mapped_column(JSON)  # metadata of the document
    content_text: Mapped[str] = mapped_column(
        Text
    )  # extracted text content of the document

    # Foreign Keys
    user_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="cases")

    question_sets: Mapped[list["QuestionSet"]] = relationship(
        "QuestionSet", back_populates="case", cascade="all, delete-orphan"
    )
    case_discussion: Mapped["CaseDiscussion"] = relationship(
        "CaseDiscussion", back_populates="case", cascade="all, delete-orphan"
    )


class QuestionSet(Base):
    """
    Question Sets group the exam questions of a specific topic for a case.
    """

    __tablename__ = "question_sets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now()
    )
    prompt_version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1
    )  # Store the version of the prompt that was used

    # Foreign Keys
    case_id: Mapped[str] = mapped_column(
        String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    prompt_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("prompts.id", ondelete="NO ACTION"), nullable=False
    )

    # Relationships
    case: Mapped["Case"] = relationship(back_populates="question_sets")
    prompt: Mapped["Prompt"] = relationship("Prompt", back_populates="question_sets")
    questions: Mapped[list["Question"]] = relationship(
        back_populates="question_set", cascade="all, delete-orphan"
    )


# Exam question model
class Question(Base):
    """
    Exam questions that the exam will cover.
    """

    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[str] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(10), nullable=False)
    _keywords: Mapped[str] = mapped_column("keywords", Text, nullable=False)
    llm_answer: Mapped[str] = mapped_column(
        Text, nullable=True
    )  # LLM_Answer is part of the Question Object
    is_answered: Mapped[bool] = mapped_column(
        Boolean, default=False
    )  # should be true when there is a user answer with status final

    # Foreign Keys
    question_set_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("question_sets.id", ondelete="CASCADE")
    )

    # Getter and Setter for keywords
    @property
    def keywords(self):
        # Convert from DB string back to list
        return json.loads(self._keywords) if self._keywords else []

    @keywords.setter
    def keywords(self, value):
        # Convert list to string for DB
        if isinstance(value, list):
            self._keywords = json.dumps(value)
        else:
            self._keywords = value

    # Relationships
    question_set: Mapped["QuestionSet"] = relationship(back_populates="questions")

    answer_discussion: Mapped["AnswerDiscussion"] = relationship(
        "AnswerDiscussion", back_populates="question", cascade="all, delete-orphan"
    )
    user_answer: Mapped["UserAnswer"] = relationship(
        "UserAnswer", back_populates="question", cascade="all, delete-orphan"
    )


class CaseDiscussion(Base):
    """
    CaseDiscussion is a collection of AnswerDiscussion objects for a case.
    """

    __tablename__ = "case_discussions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now()
    )
    last_message_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(), onupdate=lambda: datetime.now()
    )

    # Foreign Keys
    case_id: Mapped[str] = mapped_column(
        String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    case: Mapped["Case"] = relationship(back_populates="case_discussion")

    answer_discussions: Mapped[list["AnswerDiscussion"]] = relationship(
        "AnswerDiscussion",
        back_populates="case_discussion",
        cascade="all, delete-orphan",
        uselist=True,
    )


class AnswerDiscussion(Base):
    """
    AnswerDiscussion is a collection of messages for a specific question.
    """

    __tablename__ = "answer_discussions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now()
    )
    last_message_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(), onupdate=lambda: datetime.now()
    )

    # Foreign Keys
    case_discussion_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("case_discussions.id", ondelete="CASCADE"), nullable=False
    )
    question_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    case_discussion: Mapped["CaseDiscussion"] = relationship(
        "CaseDiscussion",
        back_populates="answer_discussions",
        uselist=False,
    )
    question: Mapped["Question"] = relationship(
        "Question",
        back_populates="answer_discussion",
        uselist=False,
    )
    # Relationship (1 AnswerDiscussion : n Messages)
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="answer_discussion",
        cascade="all, delete-orphan",
    )
    # Relationship (1 AnswerDiscussion : 1 UserAnswer)
    user_answer: Mapped["UserAnswer"] = relationship(
        "UserAnswer",
        back_populates="answer_discussion",
        cascade="all, delete-orphan",
        uselist=False,
    )


class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role: Mapped[MessageRole] = mapped_column(
        SQLAlchemyEnum(MessageRole, name="message_role_enum", create_type=False),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now()
    )

    # Foreign Keys
    answer_discussion_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("answer_discussions.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationships
    answer_discussion: Mapped["AnswerDiscussion"] = relationship(
        "AnswerDiscussion", back_populates="messages"
    )


class AnswerStatus(Enum):
    DISCUSSION = "discussion"
    FINAL = "final"


class UserAnswer(Base):
    __tablename__ = "user_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    condensed_answer: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # condensed answer from the discussion
    status: Mapped[AnswerStatus] = mapped_column(
        SQLAlchemyEnum(AnswerStatus, name="answer_status_enum", create_type=False),
        default=AnswerStatus.DISCUSSION,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(), onupdate=lambda: datetime.now()
    )

    # Relationships
    answer_discussion_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("answer_discussions.id", ondelete="CASCADE"),
        nullable=False,
    )
    answer_discussion: Mapped["AnswerDiscussion"] = relationship(
        "AnswerDiscussion", back_populates="user_answer"
    )

    # LLM_Answer is part of the Question Object
    question_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )
    question: Mapped["Question"] = relationship(
        "Question", back_populates="user_answer"
    )


class PromptType(Enum):
    INSTRUCTION = "instruction"
    SIMPLE = "simple"
    COMPLEX = "complex"


class PromptSpecialization(Enum):
    ALLGEMEIN = "allgemein"
    TIEFENPSYCHOLOGIE = "tiefenpsychologie"
    VERHALTENSTHERAPIE = "verhaltenstherapie"


class PromptCategory(Enum):
    RELATIONSHIPS = "relationships"
    CONFLICT = "conflict"
    STRUCTURE = "structure"


class PromptSubCategory(Enum):
    # Relationships subcategories
    CORE_CONFLICTUAL_RELATIONSHIP_THEME = "core_conflictual_relationship_theme"
    OBJECT_RELATIONS = "object_relations"
    TRANSFERENCE_COUNTERTRANSFERENCE = "transference_countertransference"
    ATTACHMENT_STYLES = "attachment_styles"

    # Conflict subcategories
    OPD_CONFLICT = "opd_conflict"
    BASIC_CONFLICTS = "basic_conflicts"
    UNCONSCIOUS_PROCESSES = "unconscious_processes"

    # Structure subcategories
    STRUCTURE_LEVEL = "structure_level"
    STRUCTURAL_DEFICITS = "structural_deficits"
    DEFENSE_MECHANISMS = "defense_mechanisms"
    DEVELOPMENTAL_ASPECTS = "developmental_aspects"


class Prompt(Base):
    __tablename__ = "prompts"

    id: Mapped[str] = mapped_column(
        String(64), primary_key=True
    )  # Example: "examiner_system_rules_v1", "user_task_generate_questions_cardiology"
    type: Mapped[PromptType] = mapped_column(
        SQLAlchemyEnum(PromptType, name="prompt_type_enum", create_type=False),
        nullable=False,
    )  # 'instruction', 'simple', 'complex'
    role: Mapped[MessageRole] = mapped_column(
        SQLAlchemyEnum(MessageRole, name="message_role_enum", create_type=False),
        default=MessageRole.SYSTEM,
        nullable=False,
    )  # 'all prompts are system prompts'
    specialization: Mapped[PromptSpecialization] = mapped_column(
        SQLAlchemyEnum(
            PromptSpecialization, name="prompt_specialization_enum", create_type=False
        ),
        nullable=True,
    )  # Example: tiefenpsychologie, verhaltenstherapie, etc.
    category: Mapped[PromptCategory] = mapped_column(
        SQLAlchemyEnum(PromptCategory, name="prompt_category_enum", create_type=False),
        nullable=True,
    )  # Example: relationship, conflict
    sub_category: Mapped[PromptSubCategory] = mapped_column(
        SQLAlchemyEnum(
            PromptSubCategory, name="prompt_subcategory_enum", create_type=False
        ),
        nullable=True,
    )  # Example: opd_conflict, core_conflictual_relationship_theme
    content: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # The actual prompt text, possibly with placeholders
    version: Mapped[int] = mapped_column(
        Integer, default=1
    )  # Incremented when the prompt is updated
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(), onupdate=lambda: datetime.now()
    )

    # Relationships
    question_sets: Mapped[list["QuestionSet"]] = relationship(
        "QuestionSet", back_populates="prompt"
    )
