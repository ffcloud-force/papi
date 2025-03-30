import pytest
from fastapi.testclient import TestClient
from backend.api.main import app
import json

from backend.services.case_service import CaseService

client = TestClient(app)

@pytest.mark.asyncio
async def test_upload_case(client, test_user, auth_headers, monkeypatch):
    # Mock LLM service to return predictable results
    async def mock_generate_all_questions_and_answers_async(self, user_id, case_id):
        from backend.database.persistent.models import ExamQuestion
        
        question = ExamQuestion(
            question="Test question 1?",
            context="Test context",
            difficulty="easy",
            keywords=json.dumps(["test", "question"]),
            general_type="knowledge", 
            specific_type="recall"
        )
        
        return {"Topic 1": [question]}
    
    from backend.services.llm_service import LLMService
    monkeypatch.setattr(LLMService, "generate_all_questions_and_answers_async", 
                        mock_generate_all_questions_and_answers_async)
    
    case_service = CaseService()

    # Load a small valid PDF file from the test resources
    with open("backend/tests/integration/resources/minimal.pdf", "rb") as f:
        file_data = f.read()

    # Upload a case
    case_number = 1
    filename = "test_case.pdf"  # Changed to .pdf since the service checks for this extension

    # Process the case
    await case_service.process_case_async_and_store_case_and_qanda(file_data, filename, test_user.id, case_number)

    # Check if case was added to the database
    from backend.database.persistent.models import Case, CaseStatus
    from backend.database.persistent.config import get_db
    db = next(get_db())
    case = db.query(Case).filter(Case.user_id == test_user.id).first()
    
    print(f"Case ID: {case.id}")
    print(f"Testing URL: /cases/get_case_questions/{case.id}")

    assert case is not None
    assert case.filename == filename
    assert case.case_number == case_number
    assert case.status == CaseStatus.COMPLETED  # Assuming this is the final status
    
    # Test a simple endpoint first to verify the router is working
    root_response = client.get("/")
    print(f"Root response: {root_response.status_code}, {root_response.text}")

    # Now try the cases endpoint
    response = client.get(f"/cases/get_case_questions/{case.id}", headers=auth_headers)
    print(f"Case questions response: {response.status_code}, {response.text}")

    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == CaseStatus.COMPLETED
    assert len(data["question_sets"]) > 0
    
    # Verify question set content
    question_set = data["question_sets"][0]
    assert "Topic 1" == question_set["topic"]
    assert len(question_set["questions"]) > 0
    
    # Verify question content
    question = question_set["questions"][0]
    assert "Test question 1?" == question["question"]
    assert "Test context" == question["context"]
    assert "easy" == question["difficulty"] 