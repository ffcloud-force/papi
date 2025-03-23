from PyPDF2 import PdfReader
from backend.modules.llm.providers.openai_singleton import get_openai_client
from backend.modules.llm.prompts.exam_prompts import (
    get_examiner_prompt, get_output_format, get_prompt_by_id, get_all_prompt_ids
)
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

    def process_answer(self, questions_str: str, general_type: str, specific_type: str = None, max_retries=2):
        """
        Parse the string output from the LLM into JSON format and validate with Pydantic.
        If validation fails, retry the query.
        
        Args:
            questions_str (str): The string output from the LLM containing JSON data
            general_type (str): The general type of the question
            specific_type (str, optional): The specific type of the question
            max_retries (int): Maximum number of retry attempts
            
        Returns:
            List[ExamQuestion]: A list of validated ExamQuestion models
        """
        
        # First attempt with the original response
        questions = self._try_process_answer(questions_str, general_type, specific_type)
        
        # If processing failed, retry with clearer instructions
        retries = 0
        while questions is None and retries < max_retries:
            print(f"Validation failed, retrying ({retries+1}/{max_retries})...")
            
            # Get prompt ID based on general_type and specific_type
            prompt_id = general_type
            if specific_type:
                prompt_id = f"{general_type}_{specific_type}"
            
            # Add more explicit instructions about the expected format
            enhanced_prompt = get_examiner_prompt()
            enhanced_prompt += get_prompt_by_id(prompt_id)
            enhanced_prompt += "Nachfolgend bekommst du den Falltext. Erstelle Fragen zu diesem Fall, welche das oben genannte Thema betreffen: "
            enhanced_prompt += "\n\n" + self.case_text
            enhanced_prompt += "\n\n" + get_output_format()
            enhanced_prompt += "\n\nWICHTIG: Stelle sicher, dass die Antwort gültiges JSON ist mit den Feldern 'question', 'context', 'difficulty' (nur 'leicht', 'mittel' oder 'schwer') und 'keywords' (als Array). Formatiere das JSON korrekt."
            
            # Retry with more explicit instructions
            questions_str = self._get_completion(enhanced_prompt, json_mode=True)
            questions = self._try_process_answer(questions_str, general_type, specific_type)
            retries += 1
        
        if questions is None:
            print(f"Failed to process answer after {max_retries} retries")
        
        return questions

    def _try_process_answer(self, questions_str: str, general_type: str, specific_type: str = None):
        """Helper method to try parsing and validating the LLM response"""
        import json
        try:
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

    def formulate_question(self, prompt_id):
        """Formulate a question for a given prompt ID"""
        if self.case_text is None:
            raise ValueError("Case text not loaded, please use load_case_document() first")

        prompt = get_examiner_prompt()
        prompt += get_prompt_by_id(prompt_id)
        prompt += "Nachfolgend bekommst du den Falltext. Erstelle Fragen zu diesem Fall, welche das oben genannte Thema betreffen: "
        prompt += "\n\n" + self.case_text
        prompt += get_output_format()

        return self._get_completion(prompt, json_mode=True)

    def generate_all_questions(self):
        """Generate questions for all prompt types"""
        results = {}
        for prompt_id in get_all_prompt_ids():
            question_str = self.formulate_question(prompt_id)
            import pdb; pdb.set_trace()
            # Extract prompt_type from prompt_id
            if "_" in prompt_id:
                parts = prompt_id.split("_", 1)
                general_type = parts[0]
                specific_type = parts[1]
            else:
                general_type = prompt_id
                specific_type = None
            
            processed_questions = self.process_answer(question_str, general_type, specific_type)
            
            # Only add to results if processing was successful
            if processed_questions is not None:
                results[prompt_id] = processed_questions
            else:
                print(f"Failed to process questions for prompt_id: {prompt_id}")
        
        return results
    
    def store_questions(self, questions: List[ExamQuestion], user_id: int, case_id: int):
        """
        Store the generated questions in the database
        
        Args:
            questions (List[ExamQuestion]): The list of exam questions to store
            user_id (int): The ID of the user who generated these questions
            case_id (int): The ID of the case document these questions are about
            
        Returns:
            QuestionSet: The created question set with all questions
        """
        from backend.database.persistent.config import SessionLocal
        from datetime import datetime
        
        # Create a new QuestionSet to group these questions
        question_set = QuestionSet(
            user_id=user_id,
            case_id=case_id,
            created_at=datetime.now()
        )
        
        # Get a database session using your existing SessionLocal
        db = SessionLocal()
        try:
            # Add and commit the question set first to get its ID
            db.add(question_set)
            db.commit()
            db.refresh(question_set)  # Refresh to get the new ID
            
            # Now add the relationship between questions and the set
            for question in questions:
                # Add the question_set_id to each question
                question.question_set_id = question_set.id
                db.add(question)
            
            # Commit all questions
            db.commit()
            return question_set
            
        except Exception as e:
            db.rollback()
            print(f"Error storing questions: {e}")
            return None
        finally:
            db.close()

    def generate_and_store_questions(self, case_id: int, user_id: int, prompt_id: str = None):
        """
        Generate and store questions for a given case
        
        Args:
            case_id (int): The ID of the case document
            user_id (int): The ID of the user generating questions
            prompt_id (str, optional): If provided, only generate questions for this prompt
            
        Returns:
            dict: A dictionary of all question sets created
        """
        # Get case file path from database
        from backend.database.persistent.config import SessionLocal
        from backend.database.persistent.models import Case  # Import your Case model
        import pdb; pdb.set_trace()
        db = SessionLocal()
        try:
            case = db.query(Case).filter(Case.id == case_id).first()
            if not case:
                raise ValueError(f"Case with ID {case_id} not found")
            
            self.load_case_document(case.file_path)
        finally:
            db.close()
        
        # Generate questions for all prompts or just the specified one
        results = {}
        prompt_ids = [prompt_id] if prompt_id else get_all_prompt_ids()
        
        for pid in prompt_ids:
            question_str = self.formulate_question(pid)
            
            # Extract prompt_type from prompt_id
            if "_" in pid:
                general_type, specific_type = pid.split("_", 1)
            else:
                general_type, specific_type = pid, None
            
            # Process the questions
            questions = self.process_answer(question_str, general_type, specific_type)
            
            # Store the questions if processing was successful
            if questions is not None:
                question_set = self.store_questions(questions, user_id, case_id)
                if question_set:
                    results[pid] = question_set
        
        return results