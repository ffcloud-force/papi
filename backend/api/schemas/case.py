from pydantic import BaseModel, validator
from typing import Dict

class CaseCreate(BaseModel):
    filename: str
    file_type: str
    file_size: int
    case_content: str
    case_number: int
    user_id: int
    case_metadata: Dict = {"upload_source": "web"}

    @validator('case_number')
    def validate_case_number(cls, v):
        if v not in [1, 2]:
            raise ValueError('case_number must be either 1 or 2')
        return v
    
    @validator('file_type')
    def validate_file_type(cls, v):
        allowed_types = ['pdf', 'docx', 'txt']
        if v.lower() not in allowed_types:
            raise ValueError(f'file_type must be one of {allowed_types}')
        return v.lower()
    
    @validator('file_size')
    def validate_file_size(cls, v, values):
        if 'file_type' in values and values['file_type'] == 'pdf' and v > 10_000_000:
            raise ValueError('PDF files cannot be larger than 10MB')
        return v
    
    
class CaseDelete(BaseModel):
    case_id: int
    user_id: int
