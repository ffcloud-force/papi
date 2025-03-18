from PyPDF2 import PdfReader
from backend.modules.llm.providers.openai_singleton import get_openai_client
from backend.modules.llm.prompts.exam_prompts import get_case_question_prompt, get_case_question_prompt_tp, get_examiner_prompt
"""
llm chat assistant

Process:
1. User writes message in the chat window
2. Check if user has written message in this session already (session should remain for 30minutes in cache)
3. If session exists, load messages from session and pass to the next llm request
4. If no session exists, load history from sql database
5. If no data exists in the sql database, create a new entry for the user_id
"""

### process case document from pdf file in /backend/data/example_cases/case1.pdf
def process_case_document(file_path="backend/data/example_cases/case1.pdf"):
    with open(file_path, "rb") as file:
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

class Assistant:
    def __init__(self):
        # Initialize LLM using the singleton
        self.llm = get_openai_client()
    
    def _get_completion(self, message):
        """Get a completion from the LLM (synchronous)"""
        return self.llm.invoke(message).content

    def process_case_document(self, general_type, specific_type, url_path):
        case_text = process_case_document(url_path)
        prompt = get_examiner_prompt()
        prompt += get_case_question_prompt_tp(general_type, specific_type)
        prompt += "Nachfolgend bekommst du den Falltext. Erstelle Fragen zu diesem Fall, welche das Thema betreffen: "
        prompt += "\n\n" + case_text
        print(prompt)
        questions = self._get_completion(prompt)
        return questions
    
if __name__ == "__main__":
    assistant = Assistant()
    print(assistant.process_case_document("relationships", "core_conflictual_relationship_theme", "backend/data/example_cases/case1.pdf"))