from backend.modules.cases.case_handler import CaseHandler
from backend.modules.cases.file_converter import FileConverter
from backend.services.llm_service import LLMService

class CaseService:
    def __init__(self):
        self.case_handler = CaseHandler()
        self.llm_service = LLMService()
    
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
            qanda = await self.llm_service.generate_all_questions_and_answers_async(user_id)
        except Exception as e:
            print(f"Error generating questions and answers: {e}")
            raise e
        
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
        s3_key, case_id = self.case_handler._upload_case_to_s3(file_data, user_id)
        
        try:
            # Convert binary data to text
            file_converter = FileConverter()
            case_content = file_converter.convert_pdf_from_bytes(file_data)
            
            # Add to database
            case = self.case_handler._add_case_to_db(filename, user_id, s3_key, case_id, case_content, case_number)
            return case, case_id
        except Exception as e:
            # Clean up S3 if database operation fails
            self.case_handler._delete_case_from_s3(s3_key)
            raise e
        
    def delete_case(self, case_id: str, user_id: str):
        """High-level business operation to delete a case"""

        # Get the case
        case = self.case_handler._get_case_by_id(case_id)

        # Check if case exists
        if not case:
            raise ValueError(f"Case {case_id} not found")
            
        # # Authorization check
        # if case.user_id != user_id:
        #     raise PermissionError("You don't have permission to delete this case")
            
        # Business rule check
        if case.status == "processing":
            raise ValueError("Cannot delete a case that is being processed")
            
        # Orchestrate deletion
        self.case_handler._delete_case_from_s3(case.storage_path)
        self.case_handler._delete_case_from_db(case_id)
        
        return {"message": "Case deleted successfully"}

    def get_all_cases_for_user(self, user_id:str):
        """
        Get all cases for a user
        """
        return self.case_handler._get_all_cases_for_user(user_id)

    def get_case_by_id(self, case_id:str):
        """
        Get a case by id
        """
        return self.case_handler._get_case_by_id(case_id)