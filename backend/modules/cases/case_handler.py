from backend.database.persistent.config import get_db
from backend.modules.cases.file_converter import FileConverter
from backend.database.persistent.models import Case
from backend.api.schemas.case import CaseCreate
from pydantic import ValidationError
import hashlib
import boto3
"""
case handler

Process:
1. User uploads case file
2. Case file is processed and stored in the database
3. A user can only upload 2 cases
4. If a user has already uploaded 2 cases, 
"""

class CaseHandler:
    def __init__(self):
        self.db = next(get_db())

    def _generate_case_id(self, user_id: int, case_text: str):
        """
        Generate a new case id
        """
        unique_string = f"{user_id}_{case_text}"
        return hashlib.sha256(unique_string.encode()).hexdigest()

    def _upload_case_to_s3(self, file_data, user_id):
        """
        Upload file data to S3
        
        Args:
            file_data: The binary content of the file
            user_id: ID of the user uploading the file
            
        Raises:
            FileExistsError: If the file already exists in S3
        """
        case_id = self._generate_case_id(user_id, file_data)
        
        # Generate a unique S3 key/path
        s3_key = f"cases/users/{user_id}/{case_id}"
        
        # Upload to S3 using the file data
        s3 = boto3.client('s3')
        try:
            s3.head_object(Bucket='cf-papi', Key=s3_key)
            # Object exists, raise a custom error
            raise FileExistsError(f"Eine Datei mit diesem Inhalt existiert bereits: {s3_key}")
        except s3.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                # Object doesn't exist, safe to upload
                s3.put_object(Bucket='cf-papi', Key=s3_key, Body=file_data)
            else:
                # Some other error occurred with the S3 request
                raise
        return s3_key  # Return the S3 path for storage in your database

    def _delete_case_from_s3(self, s3_key):
        """
        Delete a case from S3
        """
        s3 = boto3.client('s3')
        try:
            s3.delete_object(Bucket='cf-papi', Key=s3_key)
        except s3.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                # Object doesn't exist, safe to delete
                pass
            else:
                raise

    def _add_case_to_db(self, file_path, user_id, s3_key, case_content, case_number=1):
        """
        Add case to database with extracted text content and validation
        """
        # Determine file type from extension
        file_type = file_path.split('.')[-1].lower() if '.' in file_path else None
        
        try:
            # Create and validate with Pydantic
            case_model = CaseCreate(
                filename=file_path,
                file_type=file_type,
                file_size=len(case_content),
                case_content=case_content,
                case_number=case_number,
                user_id=user_id
            )
            
            # Generate ID after validation
            case_id = self._generate_case_id(user_id, file_path)
            
            # Create SQLAlchemy model instance
            case = Case(
                id=case_id,
                filename=case_model.filename,
                storage_path=s3_key,
                content_text=case_model.case_content,
                file_type=case_model.file_type,
                file_size=case_model.file_size,
                status="uploaded",
                case_number=case_model.case_number,
                case_metadata=case_model.case_metadata,
                user_id=case_model.user_id
            )
            
            try:
                self.db.add(case)
                self.db.commit()
            except Exception as e:
                print(e)
                self.db.rollback()
                raise e
            
            return case
            
        except ValidationError as e:
            print(f"Case data validation failed: {e}")
            # You can log, handle, or re-raise as needed
            raise ValueError("Invalid case data") from e

    def _delete_case_from_db(self, case_id):
        """
        Delete a case from the database
        """
        case = self.db.query(Case).filter(Case.id == case_id).first()
        if case:
            self.db.delete(case)
            self.db.commit()


if __name__ == "__main__":
    case_handler = CaseHandler()
    file_path = "backend/data/example_cases/case1.pdf"
    file_data = open(file_path, "rb").read()
    converter = FileConverter()
    case_content = converter.convert_pdf_to_text(file_path)
    case_handler.upload_case_to_s3_and_db(file_path, 1, case_content, 1)
