from fastapi import APIRouter, Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from backend.database.persistent.config import get_db
from backend.api.schemas import cases
from backend.modules.cases import case_handler

router = APIRouter()

@router.post("/upload_case")
async def upload_case(case: cases.Case, db: Session = Depends(get_db)):
    # store file in s3 cloud storage
    # store metadata in database
    # return case id
    
    try:
        s3_key = case_handler.upload_case_to_s3(file_data, user_id)
        # Continue with database storage, etc.
        return {"message": "Case uploaded successfully"}
    except FileExistsError as e:
        # Return an appropriate response to the user
        return {"error": "This file has already been uploaded", "details": str(e)}, 409  # HTTP 409 Conflict
    except Exception as e:
        # Handle other errors
        return {"error": "An error occurred uploading your file", "details": str(e)}, 500