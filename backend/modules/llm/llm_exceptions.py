class LLMError(Exception):
    """Base class for all LLM-related errors"""
    pass

class LLMAPIError(LLMError):
    """Errors from the underlying LLM API"""
    pass

class LLMParsingError(LLMError):
    """Errors when parsing LLM responses"""
    pass

class QuestionGenerationError(LLMError):
    """Errors in the question generation process"""
    pass
