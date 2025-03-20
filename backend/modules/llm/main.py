import json
from backend.modules.llm.services import generate_all_questions
from backend.modules.llm.assistant import LLM_Assistant

def main():
    case_file = "backend/data/example_cases/case1.pdf"
    questions = generate_all_questions(case_file)
    print(json.dumps(questions, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
