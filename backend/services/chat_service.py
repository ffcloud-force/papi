import random
from backend.services.llm_service import LLMService
from backend.services.database_service import DatabaseService
from backend.database.persistent.models import MessageRole
from typing import Optional, Dict, Any

"""
ChatService
-user clicks on the chat tab
-user selects a case
-check if there is an existing case discussion
-if there is, open the existing case discussion
-if there is not, open new case discussion
-user can select topic or select all (all is default)
-check if there is an unanswered question for that topic (if all is selected go through all topics in order of topic list)
...
"""


class ChatService:
    def __init__(self, db_service: DatabaseService, llm_service: LLMService):
        self.db_service = db_service
        self.llm_service = llm_service

    async def get_case_discussions(self, user_id: str, case_id: str) -> Dict[str, Any]:
        """Get existing discussions for a case"""
        # Get case discussions for this case
        case_discussions = self.db_service.get_case_discussions(case_id, user_id)

        # If no discussions found, return empty list
        if not case_discussions:
            return {"discussions": []}

        # Format response with most recent discussions first
        formatted_discussions = []
        for case_discussion in case_discussions:
            # Get the answer discussions for this case discussion
            answer_discussions = []
            for answer_discussion in case_discussion.answer_discussions:
                # Get the most recent message for this answer discussion
                messages = self.db_service.get_messages_by_answer_discussion_id(
                    answer_discussion.id
                )
                latest_message = messages[-1] if messages else None

                answer_discussions.append(
                    {
                        "id": answer_discussion.id,
                        "question_id": answer_discussion.question_id,
                        "created_at": answer_discussion.created_at.isoformat(),
                        "latest_message": {
                            "content": latest_message.content
                            if latest_message
                            else None,
                            "created_at": latest_message.created_at.isoformat()
                            if latest_message
                            else None,
                        },
                    }
                )

            formatted_discussions.append(
                {
                    "id": case_discussion.id,
                    "created_at": case_discussion.created_at.isoformat(),
                    "last_message_at": case_discussion.last_message_at.isoformat(),
                    "answer_discussions": answer_discussions,
                }
            )

        # Sort by last_message_at (most recent first)
        formatted_discussions.sort(key=lambda d: d["last_message_at"], reverse=True)

        return {"discussions": formatted_discussions}

    async def start_case_discussion(
        self, user_id: str, case_id: str, topic: Optional[str] = None
    ) -> dict[str, int]:
        """Start a new discussion for a case for a random unanswered question of a specific topic or completely random question"""
        # First create the case discussion without topic
        case_discussion = self.db_service.create_case_discussion(case_id, user_id)

        # Then get questions based on topic if provided
        if topic:
            questions = await self.db_service.get_unanswered_questions_by_topic(
                case_id, topic
            )
        else:
            questions = await self.db_service.get_all_unanswered_questions(case_id)

        if not questions:
            raise ValueError("No unanswered questions found")

        # Select a random question from the list
        selected_question = random.choice(questions)

        # Create answer discussion for the selected question
        answer_discussion = self.db_service.create_answer_discussion(
            case_discussion.id, selected_question.id
        )

        # Add first message (the selected question to the answer_discussion)
        first_message = self.db_service.create_chat_message(
            MessageRole.ASSISTANT, selected_question.question, answer_discussion.id
        )

        return {
            "case_discussion_id": case_discussion.id,
            "answer_discussion_id": answer_discussion.id,
            "first_message_id": first_message.id,
            "initial_message": selected_question.question,
        }

    async def add_user_message(self, content: str, answer_discussion_id: int) -> dict:
        """Add a user message to the discussion and generate a bot response"""
        # Store user message
        user_message = self.db_service.create_chat_message(
            role=MessageRole.USER,
            content=content,
            answer_discussion_id=answer_discussion_id,
        )

        # @TODO: Implement caching
        # Get answer discussion details to provide context for response
        chat_history = self.db_service.get_messages_by_answer_discussion_id(
            answer_discussion_id
        )

        # Generate bot response using LLM service
        bot_response = await self.llm_service.generate_response(content, chat_history)

        # Store bot response
        bot_message = self.db_service.create_chat_message(
            role=MessageRole.ASSISTANT,
            content=bot_response,
            answer_discussion_id=answer_discussion_id,
        )

        return {
            "user_message_id": user_message.id,
            "bot_message_id": bot_message.id,
            "bot_response": bot_response,
        }

    async def get_chat_history(self, answer_discussion_id: int) -> dict:
        """Get all messages for a specific answer discussion"""
        # Get answer discussion details
        answer_discussion = self.db_service.get_answer_discussion_by_id(
            answer_discussion_id
        )
        if not answer_discussion:
            raise ValueError(
                f"Answer discussion with ID {answer_discussion_id} not found"
            )

        # Get all messages for this discussion
        messages = self.db_service.get_messages_by_answer_discussion_id(
            answer_discussion_id
        )

        # Get question details
        question = self.db_service.get_question_by_id(answer_discussion.question_id)

        return {
            "answer_discussion_id": answer_discussion_id,
            "question": question,
            "messages": messages,
        }
