from pydantic import BaseModel
from backend.database.persistent.models import (
    MessageRole,
    PromptType,
    PromptSpecialization,
    PromptCategory,
    PromptSubCategory,
)
from typing import Optional


class PromptCreate(BaseModel):
    id: str
    type: PromptType
    role: Optional[MessageRole] = None
    specialization: Optional[PromptSpecialization] = None
    category: Optional[PromptCategory] = None
    sub_category: Optional[PromptSubCategory] = None
    content: str
