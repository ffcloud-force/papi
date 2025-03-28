from pydantic import BaseModel, field_validator, ConfigDict
from typing import List, Optional, Union
import json

class QuestionBase(BaseModel):
    model_config = ConfigDict(strict=True)
    question: str
    context: Optional[str] = None
    difficulty: str
    keywords: Union[List[str], str]
    
    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v):
        allowed_values = ['leicht', 'mittel', 'schwer']
        if v.lower() not in allowed_values:
            raise ValueError(f'Difficulty must be one of {allowed_values}')
        return v.lower()
    
    @field_validator('question')
    @classmethod
    def validate_question_length(cls, v):
        if len(v) < 10:
            raise ValueError('Question must be at least 10 characters')
        return v
        
    @field_validator('keywords')
    @classmethod
    def validate_keywords(cls, keywords):
        """Ensure keywords is a list of strings"""
        if isinstance(keywords, str):
            # If it's already a JSON string, parse it
            if keywords.startswith('[') and keywords.endswith(']'):
                try:
                    return json.loads(keywords)
                except:
                    # If JSON parsing fails, treat as comma-separated
                    return [k.strip() for k in keywords.split(',')]
            # Simple comma-separated string
            return [k.strip() for k in keywords.split(',')]
        # Already a list
        return keywords
    
    def model_dump(self, **kwargs):
        """Override model_dump to serialize keywords for database storage"""
        data = super().model_dump(**kwargs)
        if 'keywords' in data and isinstance(data['keywords'], list):
            data['keywords'] = json.dumps(data['keywords'])
        return data

class Answer(BaseModel):
    content: str
    
    @field_validator('content')
    @classmethod
    def validate_content_length(cls, v):
        if len(v) < 20:
            raise ValueError('Answer must be at least 20 characters')
        return v
