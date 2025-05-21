from fastapi import APIRouter, HTTPException, UploadFile, File
from backend.api.dependencies.auth import (
    current_user_dependency,
    current_user_resource_access_dependency,
)
from backend.database.persistent.models import CaseStatus
from backend.api.dependencies.case import case_service_dependency

router = APIRouter()


@router.post("/upload_case")
async def upload_case(
    case_service: case_service_dependency,
    current_user: current_user_dependency,
    file: UploadFile = File(...),
):
    """
    Upload a case to s3 and the database from a file, processes the file, generates questions + sets and answers, and stores them in the database

    Args:
        file: The file to upload
    """

    # @TODO: Add a check to see how many files the user has uploaded, if they have reached the limit, return a message saying they have reached the limit and need to delete one of the files.
    case_number = 1

    try:
        # Read file contents
        file_data = await file.read()

        # Process using our service
        await case_service.process_case_async_and_store_case_and_qanda(
            file_data=file_data,
            filename=file.filename,
            user_id=current_user.id,
            case_number=case_number,
        )

        return {"message": "Case uploaded successfully"}
    except FileExistsError as e:
        raise HTTPException(
            status_code=409, detail=f"This file has already been uploaded: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred uploading your file: {str(e)}"
        )


@router.get("/get_all_cases")
async def get_all_cases(
    current_user: current_user_dependency, case_service: case_service_dependency
):
    return case_service.get_all_cases_for_user(current_user.id)


@router.delete("/delete_case/{case_id}")
async def delete_case(
    case_id: str,
    case_service: case_service_dependency,
    current_user: current_user_dependency,
):
    try:
        case_service.delete_case(case_id, current_user.id)
        return {"message": "Case deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/get_case/{case_id}")
async def get_case(
    case_id: str, case_service: case_service_dependency, _: current_user_dependency
):
    return case_service.get_case_by_id(case_id)


@router.get("/get_case_questions/{case_id}")
async def get_case_questions(
    case_id: str,
    case_service: case_service_dependency,
    _: current_user_resource_access_dependency,
):
    # Get the case first to check its status
    case = case_service.get_case_by_id(case_id)
    if not case:
        return {"status": "error", "message": "Case not found"}

    if case.status == CaseStatus.PROCESSING:
        return {"status": "processing", "message": "Questions are being generated"}
    if case.status == CaseStatus.ERROR:
        return {
            "status": "error",
            "message": "An error occurred while generating questions",
        }
    if case.status == CaseStatus.UPLOADED:
        return {
            "status": "not_started",
            "message": "Question generation has not started",
        }

    # Get all question sets for this case
    question_sets = case_service.get_question_sets_by_case_id(case_id)

    if not question_sets:
        return {"status": "no_questions", "message": "No questions found for this case"}

    # Return the question sets with their questions
    result = []
    for question_set in question_sets:
        questions = []
        for q in question_set.questions:
            questions.append(
                {
                    "id": q.id,
                    "question": q.question,
                    "context": q.context,
                    "difficulty": q.difficulty,
                    "keywords": q.keywords,
                    "general_type": q.general_type,
                    "specific_type": q.specific_type,
                    "answer": q.answer,
                }
            )

        result.append(
            {
                "topic": question_set.topic,
                "created_at": question_set.created_at,
                "questions": questions,
            }
        )

    return {"status": "completed", "question_sets": result}
