from backend.modules.cases.case_handler import CaseHandler

class CaseService:
    def __init__(self):
        self.case_handler = CaseHandler()
    
    # PUBLIC INTERFACE
    def upload_case_to_s3_and_db(self, file_path, user_id, case_content, case_number=1):
        """
        Upload a case to S3 and the database
        """
        s3_key = self._upload_case_to_s3(file_path, user_id)
        try:
            self._add_case_to_db(file_path, user_id, s3_key, case_content, case_number)
        except Exception as e:
            # delete from s3 if case can not be added to the db
            self._delete_case_from_s3(s3_key)
            raise e
        
    def delete_case_from_s3_and_db(self, case_id):
        """
        Delete a case from S3 and the database
        """
        self._delete_case_from_s3(case_id)
        self._delete_case_from_db(case_id)