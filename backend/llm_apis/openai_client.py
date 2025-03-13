"""
Handles the conversation with the OpenAI API
"""
import os
import asyncio
from openai import AsyncOpenAI, OpenAI

class OpenAiClient:
    """
    A class to handle interactions with the OpenAI API.
    It uses the OpenAI API to generate text completions with the provided openai key.
    """

    """
    init method, runs once when the bot is initialized
    all connections (for one pod) use the same instance to keep memory usage low
    """
    def __init__(self, api_key=os.getenv("OPENAI_API_KEY")):
        self.client = OpenAI(api_key=api_key)
        self.async_client = AsyncOpenAI(api_key=api_key)

    """
    get_completion method, uses the OpenAI API to generate text completions
    """
    def get_completion(self, messages, model="gpt-4o-mini"):
        return self.client.chat.completions.create(messages=messages, model=model)

    """
    get_completion_async method, uses the OpenAI API to generate text completions asynchronously
    """
    async def get_completion_async(self, messages, model="gpt-4o-mini"):
        return await self.async_client.chat.completions.create(messages=messages, model=model)

if __name__ == "__main__":
    client = OpenAiClient()
    
    async def main():
        result = await client.get_completion_async([{"role": "user", "content": "Hello, how are you?"}])
        print(result)
    
    asyncio.run(main())
