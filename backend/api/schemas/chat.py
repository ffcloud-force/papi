from pydantic import BaseModel, ConfigDict

class CreateExamQuestionChat(BaseModel):
    model_config = ConfigDict(strict=True)
    question_id: int
    chat: list[dict]

# Chat message schema
class ChatMessage(BaseModel):
    model_config = ConfigDict(strict=True)
    message: str
    user_id: str
    
    