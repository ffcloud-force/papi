from backend.handler.llm.providers.openai_singleton import get_openai_client
from backend.handler.llm.llm_exceptions import LLMAPIError, RateLimitError
from langchain_core.messages import BaseMessage
import json
import asyncio
import time
import random
import re


class LLMHandler:
    """Handles low-level LLM operations and data access"""

    def __init__(self, llm: get_openai_client):
        self.llm = llm

    def _get_completion(self, message, json_mode=False):
        """Get a completion from the LLM (synchronous)"""
        max_retries = 5
        base_delay = 1

        for attempt in range(max_retries):
            try:
                if json_mode:
                    return self.llm.invoke(
                        message, response_format={"type": "json_object"}
                    ).content
                return self.llm.invoke(message).content
            except Exception as e:
                error_str = str(e)
                print(f"Error: {error_str}")
                # Check if this is a rate limit error
                if "rate_limit_exceeded" in error_str:
                    # Extract the suggested wait time if available
                    wait_time_match = re.search(
                        r"Please try again in (\d+\.\d+)s", error_str
                    )
                    if wait_time_match:
                        wait_time = float(wait_time_match.group(1))
                    else:
                        # Calculate exponential backoff with jitter
                        wait_time = (base_delay * (2**attempt)) + (
                            random.random() * 0.5
                        )

                    print(
                        f"Rate limit reached. Waiting {wait_time:.2f} seconds before retry. Attempt {attempt + 1}/{max_retries}"
                    )
                    time.sleep(wait_time)
                    continue
                # Log technical details
                print(f"LLM API Error: {error_str}")
                # Wrap in domain-specific exception
                raise LLMAPIError(
                    f"Failed to get completion from language model: {error_str}"
                ) from e

        # If we've exhausted all retries
        raise RateLimitError("Maximum retry attempts reached due to rate limiting")

    async def _get_completion_async(self, messages: list[BaseMessage], json_mode=False):
        """Get a completion from the LLM (asynchronous)"""
        max_retries = 10
        base_delay = 1

        for attempt in range(max_retries):
            try:
                if json_mode:
                    response = await self.llm.ainvoke(
                        messages, response_format={"type": "json_object"}
                    )
                    return response.content
                response = await self.llm.ainvoke(messages)
                return response.content
            except Exception as e:
                error_str = str(e)
                # Check if this is a rate limit error
                if "rate_limit_exceeded" in error_str:
                    # Extract the suggested wait time if available
                    wait_time_match = re.search(
                        r"Please try again in (\d+\.\d+)s", error_str
                    )
                    if wait_time_match:
                        wait_time = float(wait_time_match.group(1))
                    else:
                        # Calculate exponential backoff with jitter
                        wait_time = (base_delay * (2**attempt)) + (
                            random.random() * 0.5
                        )

                    print(
                        f"Rate limit reached. Waiting {wait_time:.2f} seconds before retry. Attempt {attempt + 1}/{max_retries}"
                    )
                    await asyncio.sleep(wait_time)
                    continue
                # Log technical details
                print(f"Async LLM API Error: {error_str}")
                # Wrap in domain-specific exception
                raise LLMAPIError(
                    f"Failed to get async completion from language model: {error_str}"
                ) from e

        # If we've exhausted all retries
        raise RateLimitError("Maximum retry attempts reached due to rate limiting")

    def _extract_questions(self, questions_str):
        """Extract questions from LLM response without requiring answers"""
        try:
            # Try to find JSON content within the string if needed
            start_idx = questions_str.find("{")
            end_idx = questions_str.rfind("}") + 1

            if start_idx != -1 and end_idx != -1:
                json_str = questions_str[start_idx:end_idx]
                data = json.loads(json_str)
            else:
                data = json.loads(questions_str)

            # Structure the data
            if "questions" not in data:
                if isinstance(data, list):
                    questions = data
                else:
                    questions = [data]
            else:
                questions = data["questions"]

            # Validate each question has required fields
            valid_questions = []
            for q in questions:
                if all(field in q for field in ["question", "difficulty", "keywords"]):
                    valid_questions.append(q)
                else:
                    print(f"Missing required fields in question: {q}")

            return valid_questions

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None
        except Exception as e:
            print(f"Error validating data: {e}")
            return None
