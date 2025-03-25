"""
Basic database models for users and documents
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator, JSON
from typing import Optional, List
from pydantic import BaseModel, Field
from sqlalchemy.ext.declarative import declarative_base
import json

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

# User model
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)  # Store hashed password + salt
    # password_salt = Column(String, nullable=False)  # Store password salt
    registration_date = Column(DateTime, default=datetime.now)
    last_login_date = Column(DateTime, default=datetime.now)
    
    # Relationship to cases
    cases = relationship("Case", back_populates="owner", cascade="all, delete-orphan")

# Case model
class Case(Base):
    __tablename__ = "cases"
    
    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False) # original filename
    storage_path = Column(String, nullable=False) # path to the document in the cloud storage
    upload_date = Column(DateTime, default=datetime.now)
    file_type = Column(String) # type of the file (pdf, docx, etc.)
    file_size = Column(Integer) # size of the file in bytes
    status = Column(String) # status of the document (uploaded, processed, etc.)
    case_number = Column(Integer)  # 1 or 2
    case_metadata = Column(JSON) # metadata of the document
    content_text = Column(Text) # extracted text content of the document
    
    # Relationship to user
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    owner = relationship("User", back_populates="cases") 


# Exam question model
class ExamQuestion(Base):
    __tablename__ = "exam_questions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Text, nullable=False)
    context = Column(Text, nullable=True)
    difficulty = Column(String(10), nullable=False)
    _keywords = Column("keywords", Text, nullable=False)  # Actual DB column
    general_type = Column(String(50), nullable=False)
    specific_type = Column(String(50), nullable=True)
    question_set_id = Column(Integer, ForeignKey("question_sets.id"))
    answer = Column(Text, nullable=True)
    
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
    
    # Relationship to question set
    question_set = relationship("QuestionSet", back_populates="questions")
    
    # Pydantic model for data validation
    class Config:
        orm_mode = True

# Question set model
class QuestionSet(Base):
    __tablename__ = "question_sets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    case_id = Column(String, ForeignKey("cases.id"), nullable=False)
    topic = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationship to questions
    questions = relationship("ExamQuestion", back_populates="question_set")
    
    # Pydantic model for data validation
    class Config:
        orm_mode = True
