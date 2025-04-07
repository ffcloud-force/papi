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


# class Prompt(Base):
#     """
#     Prompts are the categories of questions that the exam will cover.
#     """
#     __tablename__ = "prompts"

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     prompt = Column(Text, nullable=False)
#     specialization = Column(String(50), nullable=False)
#     general_type = Column(String(50), nullable=False)
#     specific_type = Column(String(50), nullable=True)


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
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    
    # Relationships
    owner = relationship("User", back_populates="cases")
    question_sets = relationship("QuestionSet", back_populates="case", cascade="all, delete-orphan")


class QuestionSet(Base):
    """
    Question Sets group the exam questions of a specific topic for a case.
    """
    __tablename__ = "question_sets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    topic = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    case = relationship("Case", back_populates="question_sets")
    questions = relationship("Question", back_populates="question_set", cascade="all, delete-orphan")

# Exam question model
class Question(Base):
    """
    Exam questions that the exam will cover.
    """
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_set_id = Column(Integer, ForeignKey("question_sets.id", ondelete="CASCADE"))
    question = Column(Text, nullable=False)
    context = Column(Text, nullable=True)
    difficulty = Column(String(10), nullable=False)
    _keywords = Column("keywords", Text, nullable=False)
    general_type = Column(String(50), nullable=False)
    specific_type = Column(String(50), nullable=True)
    
    # LLM_Answer is part of the Question Object
    llm_answer = Column(Text, nullable=True)
    
    # should be true when there is a user answer with status final 
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
    
    # Relationships
    question_set = relationship("QuestionSet", back_populates="questions")
    chat_session = relationship("ChatSession", back_populates="question", uselist=False)
    user_answer = relationship("UserAnswer", back_populates="question")

class ChatSession(Base):
    """
    ChatSession is a collection of AnswerDiscussion objects for a case.
    """
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    last_message_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    question = relationship("Question", back_populates="chat_session")
    answer_discussion = relationship("AnswerDiscussion", back_populates="chat_session")


class AnswerDiscussion(Base):
    """
    AnswerDiscussion is a collection of messages for a specific question.
    """
    __tablename__ = "answer_discussions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    chat_session = relationship("ChatSession", back_populates="answer_discussion")
    messages = relationship("Message", back_populates="answer_discussion")

    user_answer = relationship("UserAnswer", back_populates="answer_discussion")


class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    answer_discussion_id = Column(Integer, ForeignKey("answer_discussions.id", ondelete="CASCADE"), nullable=False)
    role = Column(SQLAlchemyEnum(MessageRole, name="message_role_enum", create_type=False), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    answer_discussion = relationship("AnswerDiscussion", back_populates="messages")

class AnswerStatus(Enum):
    DISCUSSION = "discussion"
    FINAL = "final"

class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    condensed_answer = Column(Text, nullable=False)  # condensed answer from the discussion
    status = Column(SQLAlchemyEnum(AnswerStatus, name="answer_status_enum", create_type=False), default=AnswerStatus.DISCUSSION, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    answer_discussion_id = Column(Integer, ForeignKey("answer_discussions.id", ondelete="CASCADE"), nullable=False)
    answer_discussion = relationship("AnswerDiscussion", back_populates="user_answer")
    
    # LLM_Answer is part of the Question Object
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    question = relationship("Question", back_populates="user_answer")
