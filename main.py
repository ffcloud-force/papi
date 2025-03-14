from backend.services import StorageService, DocumentProcessor
from backend.llm_apis import OpenAiClient

# The user should have the option to upload their case files
# The bot should then ask the user to select the case they want to work on
# The user should be able to select an individual case or both (only two cases are relevant for the exam – the user knows which ones)
# The bot then should ask the user questions based on the case they selected, the flow is:
# 1. Introduction
# 2. Ask the user to select the case they want to work on
# 3. Ask the first question based on the case they selected
# 4. The user should be prompted to answer the question
# 5. The bot should then give a score and tell the user what they could have done better


class Pruefungsbot:
    def __init__(self):
        self.conversation = []

    def introduce_yourself(self):
        print("Hallo, ich bin der Prüfer. Lass uns mit der ersten Frage zu deinen Fällen beginnen.")

def main():
    bot = Pruefungsbot()
    bot.introduce_yourself()
    ss = StorageService()
    
    # test upload with file from local directory
    file_path = "backend/data/example_cases/case1.pdf"
    with open(file_path, "rb") as file:
        file_data = file.read()
    
    import pdb; pdb.set_trace()
    ss.upload_document(file_data=file_data, filename=file_path, user_id="test_user", file_type=None)

if __name__ == "__main__":
    main()
