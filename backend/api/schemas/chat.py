from pydantic import BaseModel, ConfigDict

class CreateChatSession(BaseModel):
    model_config = ConfigDict(strict=True)
    user_id: str
    topic: str

# Chat message schema
class ChatMessage(BaseModel):
    model_config = ConfigDict(strict=True)
    message: str
    user_id: str
    
    