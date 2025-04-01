from backend.handler.storage.storage_handler import StorageHandler

class StorageService:
    def __init__(self):
        self.storage_handler = StorageHandler()
        
    def upload_case_to_s3(self, file_data: bytes, user_id: str):
        """
        Upload a case to S3
        """
        #@TODO: add type checking
        try:
            return self.storage_handler._upload_case_to_s3(file_data, user_id)
        except Exception as e:
            print(f"Error uploading case to S3: {e}")
            raise e
    
    def delete_case_from_s3(self, s3_key: str):
        """
        Delete a case from S3
        """
        #@TODO: add type checking
        try:
            return self.storage_handler._delete_case_from_s3(s3_key)
        except Exception as e:
            print(f"Error deleting case from S3: {e}")
            raise e
    
    def get_case_by_id_from_s3(self, user_id: str, case_id: str):
        """
        Get a case by id from S3
        """
        #@TODO: add type checking
        try:
            return self.storage_handler._get_case_by_id_from_s3(user_id, case_id)
        except Exception as e:
            print(f"Error getting case by id from S3: {e}")
            raise e
    
    