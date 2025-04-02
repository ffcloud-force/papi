
from typing import Annotated
from fastapi import APIRouter, Depends
from backend.api.dependencies.auth import current_user_dependency
from backend.api.dependencies.chat_service import chat_service_dependency

router = APIRouter()

@router.get("/ask_question")
async def ask_question(
    current_user: current_user_dependency,
    chat_service: chat_service_dependency,
):
    pass