from backend.modules.cases.case_handler import CaseHandler
from backend.modules.cases.file_converter import FileConverter

class CaseService:
    def __init__(self):
        self.case_handler = CaseHandler()
    
    def upload_case_and_generate_questions_and_answers(self, file_data: bytes, filename: str, user_id:str, case_number:int=1):
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
        s3_key = self.case_handler._upload_case_to_s3(file_data, user_id)
        
        try:
            # Convert binary data to text
            file_converter = FileConverter()
            case_content = file_converter.convert_pdf_from_bytes(file_data)
            
            # Add to database
            case = self.case_handler._add_case_to_db(filename, user_id, s3_key, case_content, case_number)
            return case
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