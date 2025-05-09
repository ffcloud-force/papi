from fastapi import APIRouter
from backend.api.dependencies.auth import current_user_dependency
from backend.api.dependencies.chat import chat_service_dependency
from backend.api.schemas.chat import MessageRequest
from typing import Optional

router = APIRouter()


@router.post("/start_case_discussion")
async def start_case_discussion(
    current_user: current_user_dependency,
    chat_service: chat_service_dependency,
    case_id: str,
    topic: Optional[str] = None,
):
    """creates case discussion, answer discussion and first message"""
    return await chat_service.start_case_discussion(current_user.id, case_id, topic)


@router.get("/case_discussions")
async def get_case_discussions(
    current_user: current_user_dependency,
    chat_service: chat_service_dependency,
    case_id: str,
):
    """Get existing discussions for a case"""
    return await chat_service.get_case_discussions(current_user.id, case_id)


@router.post("/message")
async def add_message(
    current_user: current_user_dependency,
    chat_service: chat_service_dependency,
    message: MessageRequest,
):
    """Add a user message to the discussion and generate a bot response"""
    return await chat_service.add_user_message(
        content=message.message_data, answer_discussion_id=message.answer_discussion_id
    )


@router.get("/chat_history")
async def get_chat_history(
    current_user: current_user_dependency,
    chat_service: chat_service_dependency,
    answer_discussion_id: int,
):
    """Get chat history for a specific answer discussion"""
    return await chat_service.get_chat_history(answer_discussion_id)
