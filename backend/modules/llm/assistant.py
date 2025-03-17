import asyncio
from langchain_core.prompts import ChatPromptTemplate
from backend.modules.llm.prompts.exam_prompts import get_chat_system_prompt_einzelpruefung
from backend.modules.llm.providers.openai_singleton import get_openai_client
import PyPDF2

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
def process_case_document():
    with open("backend/data/example_cases/case1.pdf", "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    return text

class Assistant:
    def __init__(self):
        # Initialize LLM using the singleton
        self.llm = get_openai_client()
        
        # Create system prompt
        self.system_prompt = get_chat_system_prompt_einzelpruefung()
        
        # Create the prompt template (without history)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{input}")
        ])
        
        # Create the conversation chain
        self.conversation = self.prompt | self.llm
    
    def get_completion(self, message):
        """Get a completion from the LLM (synchronous)"""
        return self.llm.invoke(message).content
    
    def process_document(self, document):
        """Handle a user provided case document"""
        import pdb;pdb.set_trace()
        text = process_case_document(document)
        
if __name__ == "__main__":
    assistant = Assistant()
    assistant.process_document(process_case_document())