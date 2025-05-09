from backend.services.chat_service import ChatService
from backend.api.dependencies.database import get_database_service
from backend.services.database_service import DatabaseService
from backend.api.dependencies.llm import get_llm_service
from backend.services.llm_service import LLMService
from typing import Annotated
from fastapi import Depends

def get_chat_service(
    db_service: Annotated[DatabaseService, Depends(get_database_service)],
    llm_service: Annotated[LLMService, Depends(get_llm_service)]
) -> ChatService:
    return ChatService(db_service, llm_service)

chat_service_dependency = Annotated[ChatService, Depends(get_chat_service)]