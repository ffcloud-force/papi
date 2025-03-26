from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from backend.database.persistent.config import get_db
from backend.api.schemas import case
from backend.services.case_service import CaseService

router = APIRouter()

@router.post("/upload_case")
async def upload_case(
    file: UploadFile = File(...),
    case_number: int = Form(1),
    user_id: str = Form(...),  # In production, this would come from your auth system
    db: Session = Depends(get_db)
):
    case_service = CaseService()

    try:
        # Read file contents
        file_data = await file.read()
        
        # Process using our service
        case_service.upload_case(
            file_data=file_data,
            filename=file.filename,  # We're using filename as a parameter
            user_id=user_id,
            case_number=case_number
        )
        
        return {"message": "Case uploaded successfully"}
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=f"This file has already been uploaded: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred uploading your file: {str(e)}")

@router.get("/get_all_cases")
async def get_all_cases(
    user_id: str,
    db: Session = Depends(get_db)
):
    case_service = CaseService()
    return case_service.get_all_cases_for_user(user_id)

@router.delete("/delete_case")
async def delete_case(
    case_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    case_service = CaseService()

    try:
        case_service.delete_case(case_id, user_id)
        return {"message": "Case deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred deleting your case: {str(e)}")