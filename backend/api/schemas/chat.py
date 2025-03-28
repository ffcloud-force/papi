from pydantic import BaseModel, ConfigDict

# Chat message schema
class ChatMessage(BaseModel):
    model_config = ConfigDict(strict=True)
    message: str
    user_id: str
    
    