from backend.modules.llm.llm_handler import LLMHandler
from backend.api.schemas.qanda import Question, Answer
from backend.modules.llm.prompts.exam_prompts import (
    get_examiner_prompt, get_output_format_questions, get_output_format_answers, get_prompt_by_id, 
    get_all_prompt_ids, get_examiner_prompt_answer
)
# from backend.modules.llm.prompts.exam_prompts_test import (
#     get_examiner_prompt, get_output_format_questions, get_output_format_answers, get_prompt_by_id, 
#     get_all_prompt_ids, get_examiner_prompt_answer
# )
from backend.database.persistent.models import ExamQuestion
from backend.modules.cases.file_converter import FileConverter
from backend.services.database_service import DatabaseService
import json
import sqlalchemy.exc
import asyncio

class LLMService:
    """Service layer for LLM assistant operations"""
    
    def __init__(self):
        self.llm_handler = LLMHandler()
        self.database_service = DatabaseService()
        self.file_converter = FileConverter()
        self.case_text = None
    
    #PUBLIC METHODS
    def load_case_document_from_stream(self, file_data: bytes):
        """Load case document from stream"""
        try:
            self.case_text = self.file_converter.convert_pdf_from_bytes(file_data)
        except Exception as e:
            print(f"Error loading case document from stream: {e}")
            raise e

    def load_case_document_from_database(self, case_id):
        """Load case document from database"""
        # @TODO: Implement this
        pass
    
    def load_case_document_from_s3(self, case_id):
        """Load case document from S3"""
        # @TODO: Implement this
        pass

    async def generate_all_questions_and_answers_async(self, user_id):
        """Generate questions for all prompt types asynchronously"""
        if not self.case_text:
            raise ValueError("Case text not loaded")

        results = {}
        # Get all prompt IDs
        prompt_ids = get_all_prompt_ids()
        
        # Use a semaphore to limit concurrency - adjust the value based on your needs
        # Start with a small number like 2-3 to avoid rate limits
        semaphore = asyncio.Semaphore(3)
        
        # Create tasks with semaphore control
        tasks = [self._process_with_semaphore(
            semaphore, 
            self._generate_questions_and_answers_async, 
            prompt_id, 
            user_id
        ) for prompt_id in prompt_ids]
        
        # Execute tasks with concurrency control
        completed_tasks = await asyncio.gather(*tasks)
        
        # Process results - handle exceptions properly here
        for result, prompt_id in completed_tasks:
            if result is not None:
                results[prompt_id] = result
                print(f"Completed processing for prompt: {prompt_id}")
            else:
                print(f"No results for prompt: {prompt_id}")

        return results
    
    # Keep the sync version for compatibility
    def generate_all_questions_and_answers(self, user_id):
        """Generate questions for all prompt types (synchronous version)"""
        if not self.case_text:
            raise ValueError("Case text not loaded")
            
        results = {}
        for prompt_id in get_all_prompt_ids():
            print(f"Processing prompt: {prompt_id}")
            questions = self._generate_questions_and_answers(prompt_id, user_id)
            if questions:
                results[prompt_id] = questions
                
        return results
    
    def store_questions_and_set(self, questions: dict[str, list[ExamQuestion]], user_id: int, case_id: int):
        """Store the generated questions in the database using DatabaseService"""
        try:
            # Use the database service to store questions
            question_sets = self.database_service.create_questions_and_set(
                questions, user_id, case_id
            )
            return question_sets
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

    def _generate_questions_and_answers(self, prompt_id, user_id):
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
                    raw_q, answer, general_type, specific_type, user_id
                )
                processed_questions.append(question)
                
            except Exception as e:
                print(f"Error processing question: {e}")

        return processed_questions
    
    async def _generate_questions_and_answers_async(self, prompt_id, user_id):
        """Generate questions with answers for a specific prompt asynchronously"""
        # Get raw questions
        raw_questions, general_type, specific_type = await self._generate_questions_for_prompt_async(prompt_id)
        
        if not raw_questions:
            return []
            
        # Process each question individually with answers
        # Use a semaphore to limit concurrency for question processing
        question_semaphore = asyncio.Semaphore(2)
        
        # Create tasks with semaphore control
        tasks = [self._process_with_semaphore(
            question_semaphore,
            self._process_question_async,
            raw_q,
            general_type, 
            specific_type, 
            user_id
        ) for raw_q in raw_questions]
        
        # Run all answer generations with controlled concurrency
        processed_results = await asyncio.gather(*tasks)
        
        # Filter out None results (from errors) and extract just the first element of the tuple
        return [result for result, _ in processed_results if result is not None]

    async def _process_question_async(self, raw_q, general_type, specific_type, user_id):
        """Process a single question asynchronously"""
        try:
            # Generate answer
            answer = await self._generate_answer_for_question_async(raw_q["question"])
            
            # Create question object
            question = self._create_exam_question_object(
                raw_q, answer, general_type, specific_type, user_id
            )
            return question
        except Exception as e:
            print(f"Error processing question: {e}")
            return None

    #PRIVATE LOWLEVEL METHODS

    async def _process_with_semaphore(self, semaphore, processing_func, item, *args):
        """Generic semaphore-controlled processing function
        
        Args:
            semaphore: The semaphore to control concurrency
            processing_func: The async function to call
            item: The primary item to process (prompt_id or question)
            *args: Additional arguments to pass to the processing function
        """
        async with semaphore:
            try:
                result = await processing_func(item, *args)
                return result, item
            except Exception as e:
                print(f"Error processing {item}: {str(e)}")
                return None, item

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

    def _create_exam_question_object(self, raw_question, answer, general_type, specific_type, user_id):
        """Create an ExamQuestion object from raw question data"""
        # Let the model handle conversion through its property
        return ExamQuestion(
            question=raw_question["question"],
            context=raw_question.get("context"),
            difficulty=raw_question["difficulty"],
            keywords=raw_question["keywords"],  # Let the ExamQuestion model handle conversion
            general_type=general_type,
            specific_type=specific_type,
            answer=answer,
            user_id=user_id
        )