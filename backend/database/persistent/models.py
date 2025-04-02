import uuid
import json
from enum import Enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator, JSON
from backend.database.persistent.config import Base


# For SQLite compatibility with JSON
class JSONType(TypeDecorator):
    impl = Text
    
    def process_bind_param(self, value, dialect):
        import json
        if value is not None:
            value = json.dumps(value)
        return value
        
    def process_result_value(self, value, dialect):
        import json
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
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    email_verified = Column(Boolean, default=True) #@TODO: set to false once email verification is implemented
    password_hash = Column(String, nullable=False)  # Store hashed password + salt
    role = Column(SQLAlchemyEnum(UserRole, name="user_role_enum", create_type=False), default=UserRole.USER, nullable=False)
    registration_date = Column(DateTime, default=datetime.now)
    last_login_date = Column(DateTime, default=datetime.now)
    
    # All direct relationships
    cases = relationship("Case", back_populates="owner", cascade="all, delete-orphan")
    question_sets = relationship("QuestionSet", back_populates="user", cascade="all, delete-orphan")
    questions = relationship("ExamQuestion", back_populates="user", cascade="all, delete-orphan")  # New direct relationship
    exam_answers = relationship("ExamQuestionAnswer", back_populates="user", cascade="all, delete-orphan")

class CaseStatus(Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# Case model
class Case(Base):
    __tablename__ = "cases"
    
    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False) # original filename
    storage_path = Column(String, nullable=False) # path to the document in the cloud storage
    upload_date = Column(DateTime, default=datetime.now)
    file_type = Column(String) # type of the file (pdf, docx, etc.)
    file_size = Column(Integer) # size of the file in bytes
    status = Column(SQLAlchemyEnum(CaseStatus, name="case_status_enum", create_type=False), default=CaseStatus.UPLOADED, nullable=False) # status of the document (uploaded, processed, etc.)
    case_number = Column(Integer)  # 1 or 2
    case_metadata = Column(JSON) # metadata of the document
    content_text = Column(Text) # extracted text content of the document
    
    # Relationship to user
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    owner = relationship("User", back_populates="cases")
    
    # Add relationship to question sets
    question_sets = relationship("QuestionSet", back_populates="case", cascade="all, delete-orphan")

# Exam question model
class ExamQuestion(Base):
    __tablename__ = "exam_questions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_set_id = Column(Integer, ForeignKey("question_sets.id", ondelete="CASCADE"))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # Add direct user link
    question = Column(Text, nullable=False)
    context = Column(Text, nullable=True)
    difficulty = Column(String(10), nullable=False)
    _keywords = Column("keywords", Text, nullable=False)
    general_type = Column(String(50), nullable=False)
    specific_type = Column(String(50), nullable=True)
    answer = Column(Text, nullable=True)
    is_answered = Column(Boolean, default=False)
    
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
    
    # All relationships
    user = relationship("User", back_populates="questions")  # New relationship to user
    question_set = relationship("QuestionSet", back_populates="questions")
    answers = relationship("ExamQuestionAnswer", back_populates="question", cascade="all, delete-orphan")

# Question set model
class QuestionSet(Base):
    __tablename__ = "question_sets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # Keep direct user link
    topic = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # All relationships
    case = relationship("Case", back_populates="question_sets")
    user = relationship("User", back_populates="question_sets")
    questions = relationship("ExamQuestion", back_populates="question_set", cascade="all, delete-orphan")

class AnswerStatus(Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    REVIEWED = "reviewed"
    FINAL = "final"

class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"

class ExamQuestionAnswer(Base):
    __tablename__ = "exam_question_answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("exam_questions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    current_answer = Column(Text, nullable=False)  # The latest version of the answer
    status = Column(SQLAlchemyEnum(AnswerStatus, name="answer_status_enum", create_type=False), 
                   default=AnswerStatus.DRAFT, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    question = relationship("ExamQuestion", back_populates="answers")
    user = relationship("User", back_populates="exam_answers")
    discussion_messages = relationship("AnswerDiscussion", back_populates="answer", cascade="all, delete-orphan", order_by="AnswerDiscussion.created_at")

class AnswerDiscussion(Base):
    __tablename__ = "answer_discussions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    answer_id = Column(Integer, ForeignKey("exam_question_answers.id", ondelete="CASCADE"), nullable=False)
    role = Column(SQLAlchemyEnum(MessageRole, name="message_role_enum", create_type=False), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # If this message includes a new version of the answer
    is_answer_update = Column(Boolean, default=False)
    
    # Relationship
    answer = relationship("ExamQuestionAnswer", back_populates="discussion_messages")
