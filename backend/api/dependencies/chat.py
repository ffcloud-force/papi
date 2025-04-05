from backend.services.chat_service import ChatService
from typing import Annotated
from fastapi import Depends

def get_chat_service():
    return ChatService()

chat_service_dependency = Annotated[ChatService, Depends(get_chat_service)]