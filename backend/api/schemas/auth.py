from pydantic import BaseModel, ConfigDict

class Token(BaseModel):
    model_config = ConfigDict(strict=True)
    access_token: str
    token_type: str

class TokenData(BaseModel):
    model_config = ConfigDict(strict=True)
    email: str | None = None
    user_id: str | None = None

class LoginResponse(BaseModel):
    model_config = ConfigDict(strict=True)
    token: Token
    user_id: str
