import redis
import json
from backend.database.cache.models import Session
import uuid
from datetime import datetime, timedelta

"""
Session Manager

Process:
1. User writes message in the chat window
2. Check if user has written message in this session already (session should remain for 30minutes in cache)
3. If session exists, load messages from session and pass to the next llm request
4. If no session exists, load history from sql database
5. If no data exists in the sql database, create a new entry for the user_id
"""


class SessionManager:
    def __init__(self):
        self.redis_client = redis.Redis(host="localhost", port=6379, db=0)
        self.session_timeout = 1800  # 30 minutes in seconds

    def get_or_create_session(self, user_id):
        """Simple function that either gets an existing session or creates a new one"""
        session = self.get_session(user_id)
        if session:
            return session
        return self.create_session(user_id)

    def get_session(self, user_id):
        """Get a session and refresh its expiration time"""
        session_key = f"session:{user_id}"

        if not self.redis_client.exists(session_key):
            return None

        # Retrieve and deserialize the session data
        session_json = self.redis_client.get(session_key).decode("utf-8")
        session_dict = json.loads(session_json)

        # Convert to Pydantic model
        session = Session(**session_dict)

        # Update the expiration time in Redis (sliding expiration)
        self.redis_client.expire(session_key, self.session_timeout)

        # Also update the expires_at field in the session object
        session.expires_at = datetime.now() + timedelta(seconds=self.session_timeout)

        return session

    def create_session(self, user_id):
        """Create a new session for the user"""
        session_key = f"session:{user_id}"
        session = Session(
            id=str(uuid.uuid4()),
            user_id=user_id,
            messages=[],
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=self.session_timeout),
        )
        self.redis_client.set(
            session_key, session.model_dump_json(), ex=self.session_timeout
        )
        return session

    def update_session(self, session):
        """Update a session in Redis and refresh its expiration time"""
        session_key = f"session:{session.user_id}"

        # Update expires_at field
        session.expires_at = datetime.now() + timedelta(seconds=self.session_timeout)

        # Save to Redis with refreshed expiration
        self.redis_client.set(
            session_key, session.model_dump_json(), ex=self.session_timeout
        )

        return session


if __name__ == "__main__":
    session_manager = SessionManager()
    print(session_manager.get_or_create_session("124"))
    session_manager.update_session(session_manager.get_or_create_session("124"))
