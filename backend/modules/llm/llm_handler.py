from backend.modules.llm.providers.openai_singleton import get_openai_client
from backend.modules.llm.llm_exceptions import LLMAPIError
import json

class LLMHandler:
    """Handles low-level LLM operations and data access"""
    
    def __init__(self):
        self.llm = get_openai_client()
    
    def _get_completion(self, message, json_mode=False):
        """Get a completion from the LLM (synchronous)"""
        try:
            if json_mode:
                return self.llm.invoke(
                    message, 
                    response_format={"type": "json_object"}
                ).content
            return self.llm.invoke(message).content
        except Exception as e:
            # Log technical details
            print(f"LLM API Error: {str(e)}")
            # Wrap in domain-specific exception
            raise LLMAPIError(f"Failed to get completion from language model: {str(e)}") from e
    
    async def _get_completion_async(self, message, json_mode=False):
        """Get a completion from the LLM (asynchronous)"""
        try:
            if json_mode:
                response = await self.llm.ainvoke(
                    message, 
                    response_format={"type": "json_object"}
                )
                return response.content
            response = await self.llm.ainvoke(message)
            return response.content
        except Exception as e:
            # Log technical details
            print(f"Async LLM API Error: {str(e)}")
            # Wrap in domain-specific exception
            raise LLMAPIError(f"Failed to get async completion from language model: {str(e)}") from e
    
    def _extract_questions(self, questions_str):
        """Extract questions from LLM response without requiring answers"""
        try:
            # Try to find JSON content within the string if needed
            start_idx = questions_str.find('{')
            end_idx = questions_str.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = questions_str[start_idx:end_idx]
                data = json.loads(json_str)
            else:
                data = json.loads(questions_str)
                
            # Structure the data
            if 'questions' not in data:
                if isinstance(data, list):
                    questions = data
                else:
                    questions = [data]
            else:
                questions = data["questions"]
                
            # Validate each question has required fields
            valid_questions = []
            for q in questions:
                if all(field in q for field in ["question", "difficulty", "keywords"]):
                    valid_questions.append(q)
                else:
                    print(f"Missing required fields in question: {q}")
                    
            return valid_questions
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None
        except Exception as e:
            print(f"Error validating data: {e}")
            return None
