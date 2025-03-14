from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str

class UserCreate(UserBase):
    password: str = Field(
        min_length=8, 
        max_length=20, 
        description=
        "Password must be between 8 and 20 characters, contain at least one uppercase letter, one lowercase letter, and one number"
    )

class UserResponse(UserBase):
    id: str
    registration_date: datetime
    last_login_date: datetime

    class Config:
        orm_mode = True

class UserUpdate(UserBase):
    first_name: Optional[str]
    last_name: Optional[str]
    password: Optional[str] = Field(
        min_length=8, 
        max_length=20, 
        description=
        "Password must be between 8 and 20 characters, contain at least one uppercase letter, one lowercase letter, and one number"
    )
    email: Optional[EmailStr] = Field(
        description="Email must be a valid email address"
    )