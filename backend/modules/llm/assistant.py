from PyPDF2 import PdfReader
from backend.modules.llm.providers.openai_singleton import get_openai_client
from backend.modules.llm.prompts.exam_prompts import get_examiner_prompt, get_case_question_prompt, get_case_question_prompt_tp, get_output_format
from pydantic import BaseModel, Field
from typing import List, Optional
from backend.database.persistent.models import ExamQuestion, QuestionSet
"""
llm chat assistant

Process:
1. User writes message in the chat window
2. Check if user has written message in this session already (session should remain for 30minutes in cache)
3. If session exists, load messages from session and pass to the next llm request
4. If no session exists, load history from sql database
5. If no data exists in the sql database, create a new entry for the user_id
"""

### process case document from pdf file in /backend/data/example_cases/case1.pdf
### this function has to be put in a seperate file and handle all kinds of document types
def process_case_document(file_path="backend/data/example_cases/case1.pdf"):
    with open(file_path, "rb") as file:
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

class LLM_Assistant:
    def __init__(self):
        # Initialize LLM using the singleton
        self.llm = get_openai_client()
        self.case_file_path = None
        self.case_text = None
    
    def _get_completion(self, message, json_mode=False):
        """Get a completion from the LLM (synchronous)"""
        if json_mode:
            # This tells the model to return JSON
            return self.llm.invoke(
                message, 
                response_format={"type": "json_object"}
            ).content
        return self.llm.invoke(message).content
    
    def load_case_document(self, url_path):
        """Load the case document"""
        if not self.case_file_path or self.case_file_path != url_path:
            self.case_file_path = url_path
            self.case_text = process_case_document(url_path)
        return self.case_text

    def formulate_general_case_question(self, general_type):
        """Formulate a general question for a given case"""
        if self.case_text is None:
            raise ValueError("Case text not loaded, please use load_case_document() first")

        prompt = get_examiner_prompt()
        prompt += get_case_question_prompt(general_type)
        prompt += "Nachfolgend bekommst du den Falltext. Erstelle Fragen zu diesem Fall, welche das oben genannte Thema betreffen: "
        prompt += "\n\n" + self.case_text
        prompt += get_output_format()

        return self._get_completion(prompt)
    
    def formulate_specific_case_question(self, general_type, specific_type):
        """Formulate a specific question for a given case"""
        if self.case_text is None:
            raise ValueError("Case text not loaded, please use load_case_document() first")
        
        prompt = get_examiner_prompt()
        prompt += get_case_question_prompt_tp(general_type, specific_type)
        prompt += "Nachfolgend bekommst du den Falltext. Erstelle Fragen zu diesem Fall, welche das oben genannte Thema betreffen: "
        prompt += "\n\n" + self.case_text
        prompt += get_output_format()

        return self._get_completion(prompt)

    def process_answer(self, questions_str: str, general_type: str, specific_type: str = None):
        """
        Parse the string output from the LLM into JSON format and validate with Pydantic.
        
        Args:
            questions_str (str): The string output from the LLM containing JSON data
            general_type (str): The general type of the question
            specific_type (str, optional): The specific type of the question
            
        Returns:
            List[ExamQuestion]: A list of validated ExamQuestion models
        """
        import json
        try:
            import pdb; pdb.set_trace()
            # Try to find JSON content within the string if needed
            start_idx = questions_str.find('{')
            end_idx = questions_str.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = questions_str[start_idx:end_idx]
                data = json.loads(json_str)
            else:
                data = json.loads(questions_str)
                
            # Add the types to the data
            if 'questions' not in data:
                # If the model returned an array directly, wrap it
                if isinstance(data, list):
                    data = {"questions": data}
                else:
                    data = {"questions": [data]}
                    
            data["general_type"] = general_type
            data["specific_type"] = specific_type if specific_type else None
            
            # Use the imported models
            questions = [ExamQuestion(
                question=q["question"],
                context=q.get("context"),
                difficulty=q["difficulty"],
                keywords=q["keywords"],
                general_type=general_type,
                specific_type=specific_type
            ) for q in data["questions"]]
            
            return questions
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None
        except Exception as e:
            print(f"Error validating data: {e}")
            return None

class ExamQuestion(BaseModel):
    question: str
    context: Optional[str] = None
    difficulty: str = Field(..., pattern="^(leicht|mittel|schwer)$")
    keywords: List[str]
    
class QuestionsResponse(BaseModel):
    questions: List[ExamQuestion]
    general_type: str
    specific_type: Optional[str] = None

if __name__ == "__main__":
    llm_assistant = LLM_Assistant()