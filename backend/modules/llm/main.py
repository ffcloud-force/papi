import json
from backend.modules.llm.assistant import LLM_Assistant
from backend.database.persistent.models import Case
from backend.database.persistent.config import get_db

def main():
    """Test function to generate all questions for a case"""
    case_file = "backend/data/example_cases/case1.pdf"
    # add case file to database
    import pdb; pdb.set_trace()
    db = next(get_db())
    case = Case(
        filename=case_file,
        storage_path=case_file,
        case_metadata={"case_number": 1},
        status="uploaded"
    )
    db.add(case)
    db.commit()
    assistant = LLM_Assistant()
    assistant.load_case_document(case_file)
    return assistant.generate_and_store_questions(case_id=1, user_id=1)

if __name__ == "__main__":
    main()
