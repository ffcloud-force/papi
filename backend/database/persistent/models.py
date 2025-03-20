"""
Basic database models for users and documents
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator, JSON
from typing import Optional, List
from pydantic import BaseModel, Field

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
    
    # Relationship to documents
    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")

# Document model
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False) # original filename
    storage_path = Column(String, nullable=False) # path to the document in the cloud storage
    upload_date = Column(DateTime, default=datetime.now)
    file_type = Column(String) # type of the file (pdf, docx, etc.)
    file_size = Column(Integer) # size of the file in bytes
    status = Column(String) # status of the document (uploaded, processed, etc.)
    case_number = Column(Integer)  # 1 or 2
    document_metadata = Column(JSON) # metadata of the document
    
    # Relationship to user
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    owner = relationship("User", back_populates="documents") 


# Exam question model
class ExamQuestion(BaseModel):
    question: str
    context: Optional[str] = None
    difficulty: str = Field(..., pattern="^(leicht|mittel|schwer)$")
    keywords: List[str]
    general_type: str
    specific_type: Optional[str] = None
    
    # If needed, add SQLAlchemy model configuration
    class Config:
        orm_mode = True

class QuestionSet(BaseModel):
    id: Optional[int] = None
    case_id: int  # Reference to case document
    questions: List[ExamQuestion]
    created_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True 
