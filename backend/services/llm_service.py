from backend.modules.llm.llm_handler import LLMHandler
from backend.api.schemas.qanda import Question, Answer
# from backend.modules.llm.prompts.exam_prompts import (
#     get_examiner_prompt, get_output_format_questions, get_output_format_answers, get_prompt_by_id, 
#     get_all_prompt_ids, get_examiner_prompt_answer
# )
from backend.modules.llm.prompts.exam_prompts_test import (
    get_examiner_prompt, get_output_format_questions, get_output_format_answers, get_prompt_by_id, 
    get_all_prompt_ids, get_examiner_prompt_answer
)
from backend.database.persistent.models import ExamQuestion, QuestionSet
from backend.services.database_service import DatabaseService
from PyPDF2 import PdfReader
import json
import sqlalchemy.exc
import asyncio

class LLMService:
    """Service layer for LLM assistant operations"""
    
    def __init__(self):
        self.llm_handler = LLMHandler()
        self.database_service = DatabaseService()
        self.case_text = None
    

    #PUBLIC METHODS

    def load_case_document_from_file(self, file_path):
        """Load case document from file path"""
        with open(file_path, "rb") as file:
            pdf_reader = PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        self.case_text = text
        return text
    
    def load_case_document_from_database(self, case_id):
        """Load case document from database"""
        # @TODO: Implement this
        pass
    
    def load_case_document_from_s3(self, case_id):
        """Load case document from S3"""
        # @TODO: Implement this
        pass

    async def generate_all_questions_and_answers_async(self):
        """Generate questions for all prompt types asynchronously"""
        if not self.case_text:
            raise ValueError("Case text not loaded")
            
        results = {}
        # Create a list of tasks for all prompt types
        tasks = []
        for prompt_id in get_all_prompt_ids():
            print(f"Starting processing for prompt: {prompt_id}")
            task = self._generate_questions_and_answers_async(prompt_id)
            tasks.append(task)
        
        # Execute all tasks concurrently
        completed_tasks = await asyncio.gather(*tasks)
        
        # Process results
        for i, prompt_id in enumerate(get_all_prompt_ids()):
            questions = completed_tasks[i]
            if questions:
                results[prompt_id] = questions
                print(f"Completed processing for prompt: {prompt_id}")
                
        return results
    
    # Keep the sync version for compatibility
    def generate_all_questions_and_answers(self):
        """Generate questions for all prompt types (synchronous version)"""
        if not self.case_text:
            raise ValueError("Case text not loaded")
            
        results = {}
        for prompt_id in get_all_prompt_ids():
            print(f"Processing prompt: {prompt_id}")
            questions = self._generate_questions_and_answers(prompt_id)
            if questions:
                results[prompt_id] = questions
                
        return results
    
    def store_questions(self, questions: dict[str, list[ExamQuestion]], user_id: int, case_id: int):
        """Store the generated questions in the database using DatabaseService"""
        try:
            # Use the database service to store questions
            question_set = self.database_service.create_question_set(
                questions, user_id, case_id
            )
            return question_set
        except json.JSONDecodeError as e:
            print(f"JSON error: {e}")
            return None
        except sqlalchemy.exc.SQLAlchemyError as e:
            print(f"Database error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    #PRIVATE HIGHLEVEL METHODS

    def _generate_questions_and_answers(self, prompt_id):
        """Generate questions with answers for a specific prompt"""
        # Get raw questions
        raw_questions, general_type, specific_type = self._generate_questions_for_prompt(prompt_id)
        
        if not raw_questions:
            return []
            
        # Process each question individually with answers
        processed_questions = []
        for raw_q in raw_questions:
            try:
                # Generate answer
                answer = self._generate_answer_for_question(raw_q["question"])
                
                # Create question object
                question = self._create_exam_question_object(
                    raw_q, answer, general_type, specific_type
                )
                processed_questions.append(question)
                
            except Exception as e:
                print(f"Error processing question: {e}")

        return processed_questions
    
    async def _generate_questions_and_answers_async(self, prompt_id):
        """Generate questions with answers for a specific prompt asynchronously"""
        # Get raw questions
        raw_questions, general_type, specific_type = await self._generate_questions_for_prompt_async(prompt_id)
        
        if not raw_questions:
            return []
            
        # Process each question individually with answers
        # Create a list of tasks for all questions
        tasks = []
        for raw_q in raw_questions:
            # Create a task for generating an answer for this question
            task = self._process_question_async(raw_q, general_type, specific_type)
            tasks.append(task)
        
        # Run all answer generations concurrently
        processed_questions = await asyncio.gather(*tasks)
        
        # Filter out None results (from errors)
        return [q for q in processed_questions if q is not None]

    async def _process_question_async(self, raw_q, general_type, specific_type):
        """Process a single question asynchronously"""
        try:
            # Generate answer
            answer = await self._generate_answer_for_question_async(raw_q["question"])
            
            # Create question object
            question = self._create_exam_question_object(
                raw_q, answer, general_type, specific_type
            )
            return question
        except Exception as e:
            print(f"Error processing question: {e}")
            return None

    #PRIVATE LOWLEVEL METHODS

    async def _generate_questions_for_prompt_async(self, prompt_id):
        """Generate raw questions for a specific prompt without answers asynchronously"""
        if not self.case_text:
            raise ValueError("Case text not loaded")
            
        # Extract prompt types
        if "_" in prompt_id:
            general_type, specific_type = prompt_id.split("_", 1)
        else:
            general_type, specific_type = prompt_id, None
            
        # Create prompt for question generation
        prompt = get_examiner_prompt()
        prompt += get_prompt_by_id(prompt_id)
        prompt += "Nachfolgend bekommst du den Falltext. Erstelle Fragen zu diesem Fall, welche das oben genannte Thema betreffen: "
        prompt += "\n\n" + self.case_text
        prompt += get_output_format_questions()
        
        # Get questions from LLM asynchronously
        questions_str = await self.llm_handler._get_completion_async(prompt, json_mode=True)
        raw_questions = self.llm_handler._extract_questions(questions_str)
        
        # Validate each raw question
        validated_questions = []
        for q in raw_questions:
            valid_q = self._validate_question(q)
            if valid_q:
                validated_questions.append(valid_q)
        
        return validated_questions, general_type, specific_type

    def _generate_questions_for_prompt(self, prompt_id):
        """Generate raw questions for a specific prompt without answers (synchronous version)"""
        if not self.case_text:
            raise ValueError("Case text not loaded")
            
        # Extract prompt types
        if "_" in prompt_id:
            general_type, specific_type = prompt_id.split("_", 1)
        else:
            general_type, specific_type = prompt_id, None
            
        # Create prompt for question generation
        prompt = get_examiner_prompt()
        prompt += get_prompt_by_id(prompt_id)
        prompt += "Nachfolgend bekommst du den Falltext. Erstelle Fragen zu diesem Fall, welche das oben genannte Thema betreffen: "
        prompt += "\n\n" + self.case_text
        prompt += get_output_format_questions()
        
        # Get questions from LLM
        questions_str = self.llm_handler._get_completion(prompt, json_mode=True)
        raw_questions = self.llm_handler._extract_questions(questions_str)
        
        # Validate each raw question
        validated_questions = []
        for q in raw_questions:
            valid_q = self._validate_question(q)
            if valid_q:
                validated_questions.append(valid_q)
        
        return validated_questions, general_type, specific_type

    def _validate_question(self, raw_question):
        """Validate a question using Pydantic models"""
        try:
            # Ensure keywords is a list if it came as a string
            if isinstance(raw_question.get('keywords'), str):
                raw_question['keywords'] = [k.strip() for k in raw_question['keywords'].split(',')]
                
            # Validate with Pydantic
            validated = Question(**raw_question)
            return validated.model_dump()  # In Pydantic v2, use model_dump() instead of dict()
        except Exception as e:
            print(f"Question validation error: {str(e)}")
            return None

    async def _generate_answer_for_question_async(self, question):
        """Generate answer for a specific question asynchronously"""
        if not self.case_text:
            raise ValueError("Case text not loaded")
            
        prompt = get_examiner_prompt_answer()
        prompt += f"Question: {question}"
        prompt += "\nNachfolgend bekommst du den Falltext. Antworte auf die oben genannte Frage: "
        prompt += "\n\n" + self.case_text
        prompt += get_output_format_answers()
        
        answer_text = await self.llm_handler._get_completion_async(prompt)
        
        # Validate the answer
        try:
            validated_answer = self._validate_answer(answer_text)
            return validated_answer
        except Exception as e:
            print(f"Answer validation error: {e}")
            # Decide what to do with invalid answers - return a default?
            return "Unable to generate a valid answer."

    def _generate_answer_for_question(self, question):
        """Generate answer for a specific question (synchronous version)"""
        if not self.case_text:
            raise ValueError("Case text not loaded")
            
        prompt = get_examiner_prompt_answer()
        prompt += f"Question: {question}"
        prompt += "\nNachfolgend bekommst du den Falltext. Antworte auf die oben genannte Frage: "
        prompt += "\n\n" + self.case_text
        prompt += get_output_format_answers()
        
        answer_text = self.llm_handler._get_completion(prompt)
        
        # Validate the answer
        try:
            validated_answer = self._validate_answer(answer_text)
            return validated_answer
        except Exception as e:
            print(f"Answer validation error: {e}")
            # Decide what to do with invalid answers - return a default?
            return "Unable to generate a valid answer."

    def _validate_answer(self, answer_text):
        """Validate an answer using Pydantic models"""
        try:
            validated = Answer(content=answer_text)
            return validated.model_dump()['content']
        except Exception as e:
            print(f"Answer validation error: {str(e)}")
            return None

    def _create_exam_question_object(self, raw_question, answer, general_type, specific_type):
        """Create an ExamQuestion object from raw question data"""
        # Let the model handle conversion through its property
        return ExamQuestion(
            question=raw_question["question"],
            context=raw_question.get("context"),
            difficulty=raw_question["difficulty"],
            keywords=raw_question["keywords"],  # Let the ExamQuestion model handle conversion
            general_type=general_type,
            specific_type=specific_type,
            answer=answer
        )