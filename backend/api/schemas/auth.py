from pydantic import BaseModel
from datetime import datetime
from backend.api.schemas.user import UserResponse

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None
    user_id: str | None = None

class LoginResponse(BaseModel):
    token: Token
    user: UserResponse
    