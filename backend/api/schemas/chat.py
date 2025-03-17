from pydantic import BaseModel

# Chat message schema
class ChatMessage(BaseModel):
    message: str
    user_id: str
    
    