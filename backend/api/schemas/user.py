from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
from backend.database.persistent.models import UserRole

# User schemas
class UserBase(BaseModel):
    model_config = ConfigDict(strict=True)
    email: EmailStr
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)

    @field_validator('first_name', 'last_name')  # Apply to both fields
    def validate_name(cls, v, info):
        # info.field_name tells us which field is being validated
        field_type = info.field_name.replace('_', ' ')  # "first_name" -> "first name"
        
        if not v.strip():
            raise ValueError(f'{field_type.title()} must not be empty or whitespace')
        
        if not v.replace(' ', '').isalpha():
            raise ValueError(f'{field_type.title()} must contain only letters')
        
        return v.strip()

class UserCreate(UserBase):
    model_config = ConfigDict(strict=True)
    password: str = Field(
        min_length=8, 
        max_length=20, 
        description=
        "Password must be between 8 and 20 characters."
    )
    confirm_password: str

    @field_validator("confirm_password")
    def validate_confirm_password(cls, v, values):
        if v != values.data["password"]:
            raise ValueError("Passwords do not match")
        return v

class UserResponse(UserBase):
    id: str
    role: UserRole
    registration_date: datetime
    last_login_date: datetime

    class ConfigDict:
        from_attributes = True

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(
        None,
        min_length=8, 
        max_length=20, 
        description="Password must be between 8 and 20 characters"
    )
    current_password: Optional[str] = Field(
        None,
        description="Required when updating email or password"
    )

    @field_validator('password')
    def validate_password(cls, v):
        if v is None:
            return v
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain number')
        return v

    class ConfigDict:
        from_attributes = True

class UserDelete(UserBase):
    password: str
    confirm_password: str

    @field_validator("confirm_password")
    def validate_confirm_password(cls, v, values):
        if v != values["password"]:
            raise ValueError("Passwords do not match")
        return v

class AdminUserUpdate(UserUpdate):
    role: Optional[UserRole] = None
