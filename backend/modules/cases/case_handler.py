from backend.database.persistent.config import get_db
from backend.modules.cases.file_converter import FileConverter
from backend.database.persistent.models import Case
from backend.api.schemas.case import CaseCreate
from pydantic import ValidationError
import hashlib
import boto3

"""
This module is responsible for handling the case data.
It is responsible for uploading the case to S3 and the database.
It is also responsible for deleting the case from S3 and the database.
"""

class CaseHandler:
    def __init__(self):
        self.db = next(get_db())

    # PRIVATE METHODS #
    def _generate_case_id(self, user_id: int, case_text: str):
        """
        Generate a new case id
        """
        unique_string = f"{user_id}_{case_text}"
        return hashlib.sha256(unique_string.encode()).hexdigest()

    ## S3 operations ##
    def _upload_case_to_s3(self, file_data:bytes, user_id:str):
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
        return s3_key, case_id  # Return the S3 path and case id for storage in your database

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

    def _get_case_by_id_from_s3(self, user_id, case_id):
        """
        Get a case by id from S3
        """
        s3 = boto3.client('s3')
        s3_key = f"cases/users/{user_id}/{case_id}"
        s3.get_object(Bucket='cf-papi', Key=s3_key)
        return s3_key

    ## DB operations ##
    def _add_case_to_db(self, filename:str, user_id:str, s3_key:str, case_id:str, case_content:str, case_number:int=1):
        """
        Add case to database with extracted text content and validation
        """
        # Determine file type from extension
        file_type = filename.split('.')[-1].lower() if '.' in filename else None
        
        try:
            # Create and validate with Pydantic
            case_model = CaseCreate(
                filename=filename,
                file_type=file_type,
                file_size=len(case_content),
                case_content=case_content,
                case_number=case_number,
                user_id=user_id
            )

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

    def _update_case_status(self, case_id, status):
        """
        Update the status of a case in the database
        """
        case = self.db.query(Case).filter(Case.id == case_id).first()
        if case:
            case.status = status
            self.db.commit()
            return case
        return None

    def _delete_case_from_db(self, case_id):
        """
        Delete a case from the database
        """
        case = self.db.query(Case).filter(Case.id == case_id).first()
        if case:
            self.db.delete(case)
            self.db.commit()

    def _get_all_cases_for_user(self, user_id):
        """
        Get all cases for a user
        """
        try:
            return self.db.query(Case).filter(Case.user_id == user_id).all()
        except Exception as e:
            print(e)
            return []

    def _get_case_by_id(self, case_id):
        """
        Get a case by id
        """
        return self.db.query(Case).filter(Case.id == case_id).first()