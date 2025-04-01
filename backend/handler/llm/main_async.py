from backend.services.llm_service import LLMService
import asyncio
import time

async def main_async():
    # Start timing
    start_time = time.time()
    
    # Initialize service
    service = LLMService()
    
    # Load a case document (replace with your actual file path)
    print("Loading case document...")
    service.load_case_document_from_file("backend/data/example_cases/case1.pdf")
    
    # Generate questions and answers asynchronously
    print("Generating questions and answers asynchronously...")
    results = await service.generate_all_questions_and_answers_async()
    
    # Calculate and print elapsed time
    elapsed_time = time.time() - start_time
    print(f"Completed in {elapsed_time:.2f} seconds")
    
    # Print summary of results
    question_count = sum(len(questions) for questions in results.values())
    print(f"Generated {question_count} questions across {len(results)} topics")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(main_async())
