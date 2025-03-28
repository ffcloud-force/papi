from pydantic import BaseModel, field_validator, ConfigDict
from typing import Dict

class CaseCreate(BaseModel):
    filename: str
    file_type: str
    file_size: int
    case_content: str
    case_number: int
    user_id: str
    case_metadata: Dict = {"upload_source": "web"}

    @field_validator('case_number')
    @classmethod
    def validate_case_number(cls, v):
        if v not in [1, 2]:
            raise ValueError('case_number must be either 1 or 2')
        return v
    
    @field_validator('file_type')
    @classmethod
    def validate_file_type(cls, v):
        allowed_types = ['pdf', 'docx', 'txt']
        if v.lower() not in allowed_types:
            raise ValueError(f'file_type must be one of {allowed_types}')
        return v.lower()
    
    @field_validator('file_size')
    @classmethod
    def validate_file_size(cls, v, info):
        file_type = info.data.get('file_type')
        if file_type == 'pdf' and v > 10_000_000:
            raise ValueError('PDF files cannot be larger than 10MB')
        return v
    
    
class CaseDelete(BaseModel):
    case_id: str
    user_id: str

class CaseBase(BaseModel):
    model_config = ConfigDict(strict=True)
    title: str
    description: str
