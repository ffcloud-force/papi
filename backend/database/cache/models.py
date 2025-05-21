from pydantic import BaseModel
from datetime import datetime


class Session(BaseModel):
    id: str
    user_id: str
    messages: list[dict]
    created_at: datetime
    expires_at: datetime
