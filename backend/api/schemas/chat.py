from pydantic import BaseModel, ConfigDict, field_validator
from backend.database.persistent.models import MessageRole
from typing import Optional

class CaseDiscussionCreate(BaseModel):
    model_config = ConfigDict(strict=True)
    case_id: str
    user_id: str
    topic: Optional[str] = None

class AnswerDiscussionCreate(BaseModel):
    model_config = ConfigDict(strict=True)
    case_discussion_id: int
    question_id: int

class ChatMessageCreate(BaseModel):
    model_config = ConfigDict(strict=True)
    role: MessageRole
    content: str
    answer_discussion_id: int

    @field_validator('content', mode='before')
    @classmethod
    def validate_content(cls, v):
        #@TODO: Add chat message validation
        return v
    
class MessageRequest(BaseModel):
    answer_discussion_id: int
    message_data: str
