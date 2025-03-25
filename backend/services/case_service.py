from backend.modules.cases.case_handler import CaseHandler
from backend.modules.cases.file_converter import FileConverter

class CaseService:
    def __init__(self):
        self.case_handler = CaseHandler()

    def upload_case_to_s3_and_db(self, file_path, user_id, case_number=1):
        """
        Upload a case to S3 and the database
        """
        s3_key = self.case_handler._upload_case_to_s3(file_path, user_id)
        case_content = FileConverter().convert_pdf_to_text(file_path)
        try:
            self.case_handler._add_case_to_db(file_path, user_id, s3_key, case_content, case_number)
        except Exception as e:
            # delete from s3 if case can not be added to the db
            self.case_handler._delete_case_from_s3(s3_key)
            raise e
        
    def delete_case(self, case_id: str, user_id: int):
        """High-level business operation to delete a case"""
        # Get the case
        case = self.case_handler._get_case_by_id(case_id)
        
        # Check if case exists
        if not case:
            raise ValueError(f"Case {case_id} not found")
            
        # Authorization check
        if case.user_id != user_id:
            raise PermissionError("You don't have permission to delete this case")
            
        # Business rule check
        if case.status == "processing":
            raise ValueError("Cannot delete a case that is being processed")
            
        # Orchestrate deletion
        self.case_handler.delete_case_from_s3(case.storage_path)
        self.case_handler.delete_case_from_db(case_id)
        
        return {"message": "Case deleted successfully"}

    def get_case_by_id(self, case_id):
        """
        Get a case by id
        """
        return self.case_handler.get_case_by_id(case_id)

if __name__ == "__main__":
    cs = CaseService()
    cs.upload_case_to_s3_and_db("backend/data/example_cases/case1.pdf", 1)
    #check if case is in db
    print(cs.get_case_by_id("test"))
    cs.delete_case("test", 1)