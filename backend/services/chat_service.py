from backend.modules.chat.chat_handler import ChatHandler


class ChatService:
    def __init__(self):
        self.chat_handler = ChatHandler()

    def start_chat_session_for_topic