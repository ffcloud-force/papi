from backend.database.persistent.config import SessionLocal
from backend.database.persistent.models import User, Case, ExamQuestion, QuestionSet
from sqlalchemy.orm import Session

class DatabaseService:
    def __init__(self):
        self.db = SessionLocal()

    def get_db(self):
        return self.db

    # User-specific operations
    def create_user(self, user_data):
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        return user

    def get_user_by_id(self, user_id):
        return self.db.query(User).filter(User.id == user_id).first()

    # Case-specific operations
    def create_case(self, case_data):
        case = Case(**case_data)
        self.db.add(case)
        self.db.commit()
        return case

    def get_cases_for_user(self, user_id):
        return self.db.query(Case).filter(Case.user_id == user_id).all()

    # Question-specific operations
    def create_question_set(self, questions: dict[str, list[ExamQuestion]], user_id: int, case_id: int):
        """
        Create question sets for all topics in a single transaction.
        Each topic gets its own QuestionSet.
        
        Args:
            questions: Dictionary mapping topics to lists of ExamQuestion objects
            user_id: ID of the user creating the questions
            case_id: ID of the case these questions refer to
        """
        try:
            question_sets = {}
            
            # Begin transaction
            for topic, question_list in questions.items():
                # Create a QuestionSet for this topic
                question_set = QuestionSet(
                    user_id=user_id,
                    case_id=case_id,
                    topic=topic  # You might need to add this field to your QuestionSet model
                )
                self.db.add(question_set)
                self.db.flush()  # Get the ID without committing
                
                # Associate questions with this set
                for question in question_list:
                    question.question_set_id = question_set.id
                    self.db.add(question)
                
                question_sets[topic] = question_set
            
            # Commit everything at once
            self.db.commit()
            return question_sets
            
        except Exception as e:
            self.db.rollback()
            print(f"Error creating question sets: {str(e)}")
            raise