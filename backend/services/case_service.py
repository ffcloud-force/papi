from backend.services.storage_service import StorageService
from backend.services.database_service import DatabaseService
from backend.handler.storage.file_converter import FileConverter
from backend.services.llm_service import LLMService
from backend.database.persistent.models import CaseStatus

class CaseService:
    def __init__(self):
        self.storage_service = StorageService()
        self.llm_service = LLMService()
        self.database_service = DatabaseService()
        self.file_converter = FileConverter()

    async def process_case_async_and_store_case_and_qanda(self, file_data: bytes, filename: str, user_id:str, case_number:int=1):
        """
        Process a case to generate questions and answers, store the case and the questions and answers in the database
        
        Args:
            file_data: Binary content of the uploaded file
            filename: Original filename with extension
            user_id: ID of the user uploading
            case_number: Optional case number identifier

        Returns:
        """
        try:
            processed_case, case_id = self.upload_case(file_data, filename, user_id, case_number)
        except Exception as e:
            print(f"Error processing case: {e}")
            raise e
        
        qanda = {}
        try:
            self.llm_service.case_text = processed_case.content_text
            self.database_service.update_case_status(case_id, CaseStatus.PROCESSING)
            qanda = await self.llm_service.generate_all_questions_and_answers_async(user_id)
        except Exception as e:
            print(f"Error generating questions and answers: {e} – cleaning up case")
            self.database_service.update_case_status(case_id, CaseStatus.FAILED)
            self.storage_service.delete_case_from_s3(processed_case.storage_path)
            self.database_service.delete_case_from_db(case_id)
            raise e
        
        # change case status to completed
        self.database_service.update_case_status(case_id, CaseStatus.COMPLETED)

        try:
            self.llm_service.store_questions_and_set(qanda, user_id, case_id)
        except Exception as e:
            print(f"Error storing questions: {e}")
            raise e

    def upload_case(self, file_data: bytes, filename: str, user_id:str, case_number:int=1):
        """
        Upload a case to S3 and the database from binary file data
        
        Args:
            file_data: Binary content of the uploaded file
            filename: Original filename with extension
            user_id: ID of the user uploading
            case_number: Optional case number identifier
        """

        # Check if file is PDF (based on extension)
        if not filename.lower().endswith(".pdf"):
            raise ValueError("Only PDF files are currently supported")
        
        # Upload binary data directly to S3
        s3_key, case_id = self.storage_service.upload_case_to_s3(file_data, user_id)
        
        try:
            # Convert binary data to text
            case_content = self.file_converter.convert_pdf_from_bytes(file_data)
            
            # Add to database
            case = self.database_service.create_case(filename, user_id, s3_key, case_id, case_content, case_number)
            return case, case_id
        except Exception as e:
            # Clean up S3 if database operation fails
            self.storage_service.delete_case_from_s3(s3_key)
            raise e
        
    def delete_case(self, case_id: str, user_id: str):
        """High-level business operation to delete a case"""

        # Get the case
        case = self.database_service.get_case_by_id(case_id)

        # Check if case exists
        if not case:
            raise ValueError(f"Case {case_id} not found")

        # Business rule check
        if case.status == CaseStatus.PROCESSING:
            raise ValueError("Cannot delete a case that is being processed")
            
        # Orchestrate deletion
        self.storage_service.delete_case_from_s3(case.storage_path)
        self.database_service.delete_case_from_db(case_id)
        
        return {"message": "Case deleted successfully"}

    def get_all_cases_for_user(self, user_id:str):
        """
        Get all cases for a user
        """
        return self.database_service.get_all_cases_for_user(user_id)

    def get_case_by_id(self, case_id: str):
        """
        Get a case by its ID
        """
        return self.database_service.get_case_by_id(case_id)
        
