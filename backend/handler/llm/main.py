from backend.services.llm_service import LLMService
import time


def main():
    # Start timing
    start_time = time.time()

    llm_service = LLMService()

    # Load case document
    llm_service.load_case_document_from_file("backend/data/example_cases/case1.pdf")

    # Generate all questions
    questions = llm_service.generate_all_questions_and_answers()

    # Calculate and print elapsed time
    elapsed_time = time.time() - start_time
    print(f"Completed in {elapsed_time:.2f} seconds")

    # Print summary of results
    question_count = sum(len(questions) for questions in questions.values())
    print(f"Generated {question_count} questions across {len(questions)} topics")

    # Store in database
    llm_service.store_questions(questions, 1, 1)


if __name__ == "__main__":
    main()
