from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv(override=True)

# Singleton pattern
class OpenAIClientSingleton:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            # Add debugging here if needed
            api_key = os.getenv("OPENAI_API_KEY")
            print(f"API Key found: {api_key is not None}")
            
            cls._instance = ChatOpenAI(
                api_key=api_key,
                model="gpt-4o-mini",
                temperature=0.7,
                streaming=True
            )
        return cls._instance

# Easy access function
def get_openai_client():
    return OpenAIClientSingleton.get_instance()
