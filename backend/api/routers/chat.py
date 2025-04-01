from fastapi import APIRouter, Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from backend.database.persistent.config import get_db
from backend.api.schemas import chat
from backend.handler.llm.llm_handler import LLMHandler
from backend.handler.session.session_manager import SessionManager
from backend.api.schemas.chat import ChatMessage

router = APIRouter()
session_manager = SessionManager()

@router.post("/")
async def chat_endpoint(chat_message: ChatMessage):
    # Get or create session for this user
    llm_handler = LLMHandler()
    
    # Process the message with the user's Assistant instance
    response = await llm_handler._get_completion_async(chat_message.message)
    print(response)
    return {"message": response}
