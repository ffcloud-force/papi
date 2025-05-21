from backend.handler.llm.llm_handler import LLMHandler
from backend.api.schemas.qanda import Question, Answer
from backend.database.persistent.models import Question as QuestionSQL, PromptType
from backend.handler.storage.file_converter import FileConverter
from backend.services.database_service import DatabaseService
from backend.database.persistent.models import Message as Message
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from typing import Optional
import json
import sqlalchemy.exc
import asyncio


class LLMService:
    """Service layer for LLM assistant operations"""

    def __init__(
        self,
        llm_handler: LLMHandler,
        db_service: DatabaseService,
        file_converter: FileConverter,
    ):
        self.llm_handler = llm_handler
        self.db_service = db_service
        self.file_converter = file_converter

        self.case_text = None

    # PUBLIC METHODS
    async def generate_response(
        self, message: str, chat_history: Optional[list[Message]] = None
    ):
        """Generate a bot response to a message, incorporating chat history if provided"""
        formatted_chat_history = self._format_chat_history(chat_history)
        # @TODO: Add System prompt with case text (maybe only the relevant parts), and instructions for the LLM
        # @TODO: Add new message to chat_history
        return await self.llm_handler._get_completion_async(formatted_chat_history)

    def load_case_document_from_stream(self, file_data: bytes):
        """Load case document from stream"""
        try:
            self.case_text = self.file_converter.convert_pdf_from_bytes(file_data)
        except Exception as e:
            print(f"Error loading case document from stream: {e}")
            raise e

    async def generate_all_questions_and_answers_async(self, user_id):
        """Generate questions for all prompt types asynchronously"""
        if not self.case_text:
            raise ValueError("Case text not loaded")

        results = {}

        # Get all prompts
        question_prompts = self.db_service.get_all_prompts_by_type_negative(
            PromptType.INSTRUCTION
        )

        # Use a semaphore to limit concurrency
        semaphore = asyncio.Semaphore(3)

        # Create tasks with semaphore control
        tasks = [
            self._process_with_semaphore(
                semaphore,
                self._generate_questions_and_answers_async,
                prompt,
            )
            for prompt in question_prompts
        ]

        # Execute tasks with concurrency control
        completed_tasks = await asyncio.gather(*tasks)

        # Process results - handle exceptions properly here
        for result, prompt_id in completed_tasks:
            if result is not None:
                results[prompt_id] = result
                print(f"Completed processing for prompt: {prompt_id.id}")
            else:
                print(f"No results for prompt: {prompt_id.id}")

        return results

    def store_questions_and_set(
        self, questions: dict[str, list[Question]], case_id: int
    ):
        """Store the generated questions in the database using DatabaseService"""
        try:
            # Use the database service to store questions
            return self.db_service.create_questions_and_set(questions, case_id)
        except json.JSONDecodeError as e:
            print(f"JSON error: {e}")
            return None
        except sqlalchemy.exc.SQLAlchemyError as e:
            print(f"Database error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    # PRIVATE HIGHLEVEL METHODS
    async def _generate_questions_and_answers_async(self, prompt):
        """Generate questions with answers for a specific prompt asynchronously"""
        # Get raw questions
        raw_questions = await self._generate_questions_for_prompt_async(prompt)

        if not raw_questions:
            return []

        # Process each question individually with answers
        # Use a semaphore to limit concurrency for question processing
        question_semaphore = asyncio.Semaphore(2)

        # Create tasks with semaphore control
        tasks = [
            self._process_with_semaphore(
                question_semaphore, self._process_question_async, raw_q
            )
            for raw_q in raw_questions
        ]

        # Run all answer generations with controlled concurrency
        processed_results = await asyncio.gather(*tasks)

        # Filter out None results (from errors) and extract just the first element of the tuple
        return [result for result, _ in processed_results if result is not None]

    async def _process_question_async(self, raw_q):
        """Process a single question asynchronously"""
        try:
            # Generate answer
            answer = await self._generate_answer_for_question_async(raw_q["question"])

            # Create question object
            return self._create_question_object(raw_q, answer)
        except Exception as e:
            print(f"Error processing question: {e}")
            return None

    # PRIVATE LOWLEVEL METHODS
    def _format_chat_history(self, chat_history: list[Message]) -> list[BaseMessage]:
        """Format chat history for the LLM"""
        return [
            HumanMessage(content=m.content)
            if m.role == "user"
            else AIMessage(content=m.content)
            for m in chat_history
        ]

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

    async def _generate_questions_for_prompt_async(self, prompt):
        """Generate raw questions for a specific prompt asynchronously"""
        if not self.case_text:
            raise ValueError("Case text not loaded")

        # Construct a single, well-structured prompt
        prompt_content = (
            f"{self.db_service.get_prompt_by_id('examiner_prompt_question').content}\n\n"
            f"{prompt.content}\n\n"
            f"Nachfolgend bekommst du den Falltext. Erstelle Fragen zu diesem Fall, welche das oben genannte Thema betreffen:\n\n"
            f"{self.case_text}\n\n"
            f"{self.db_service.get_prompt_by_id('output_format_questions').content}"
        )

        # Get questions from LLM asynchronously
        questions_str = await self.llm_handler._get_completion_async(
            [SystemMessage(content=prompt_content)], json_mode=True
        )
        raw_questions = self.llm_handler._extract_questions(questions_str)

        # Validate each raw question
        validated_questions = []
        for q in raw_questions:
            valid_q = self._validate_question(q)
            if valid_q:
                validated_questions.append(valid_q)

        return validated_questions

    def _validate_question(self, raw_question):
        """Validate a question using Pydantic models"""
        try:
            # Ensure keywords is a list if it came as a string
            if isinstance(raw_question.get("keywords"), str):
                raw_question["keywords"] = [
                    k.strip() for k in raw_question["keywords"].split(",")
                ]

            # Validate with Pydantic using model_validate
            validated = Question.model_validate(raw_question)
            return validated.model_dump()
        except Exception as e:
            print(f"Question validation error: {str(e)}")
            return None

    async def _generate_answer_for_question_async(self, question):
        """Generate answer for a specific question asynchronously"""
        if not self.case_text:
            raise ValueError("Case text not loaded")

        prompt_content = (
            f"{self.db_service.get_prompt_by_id('examiner_prompt_answer').content}\n\n"
            f"Question: {question}\n\n"
            f"Nachfolgend bekommst du den Falltext. Antworte auf die oben genannte Frage: \n\n"
            f"{self.case_text}\n\n"
            f"{self.db_service.get_prompt_by_id('output_format_answers').content}"
        )

        answer_text = await self.llm_handler._get_completion_async(
            [SystemMessage(content=prompt_content)]
        )

        # Validate the answer
        try:
            return self._validate_answer(answer_text)
        except Exception as e:
            print(f"Answer validation error: {e}")
            # Decide what to do with invalid answers - return a default?
            return "Unable to generate a valid answer."

    def _validate_answer(self, answer_text):
        """Validate an answer using Pydantic models"""
        try:
            validated = Answer.model_validate({"content": answer_text})
            return validated.model_dump()["content"]
        except Exception as e:
            print(f"Answer validation error: {str(e)}")
            return None

    def _create_question_object(self, raw_question, answer):
        """Create a Question object from raw question data"""
        # Let the model handle conversion through its property
        return QuestionSQL(
            question=raw_question["question"],
            context=raw_question.get("context"),
            difficulty=raw_question["difficulty"],
            keywords=raw_question["keywords"],
            llm_answer=answer,
        )
