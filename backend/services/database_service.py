from backend.database.persistent.config import SessionLocal
from backend.database.persistent.models import User, Case, ExamQuestion, QuestionSet
from backend.api.schemas.qanda import QuestionRetrieve
from backend.modules.database.database_handler import DatabaseHandler

class DatabaseService:
    def __init__(self):
        self.db = SessionLocal()
        self.db_handler = DatabaseHandler()

    # User-specific operations
    def create_user(self, user_data):
        # TODO: Add validation
        return self.db_handler.create_user(user_data)

    def get_user_by_id(self, user_id):
        # TODO: Add validation
        return self.db_handler.get_user_by_id(user_id)

    # Case-specific operations
    def create_case(self, case_data):
        # TODO: Add validation
        return self.db_handler.create_case(case_data)

    def get_cases_for_user(self, user_id):
        # TODO: Add validation
        return self.db.query(Case).filter(Case.user_id == user_id).all()

    # Question-specific operations
    def create_questions_and_set(self, questions: dict[str, list[ExamQuestion]], user_id: int, case_id: int):
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
                    topic=topic
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

    def get_questions_by_topic_for_user(self, case_id: str, general_type: str, specific_type: str, user_id: str) -> list[dict]:
        """
        Get questions by topic for a user

        Args:
            case_id: ID of the case
            general_type: General type of the questions
            specific_type: Specific type of the questions
            user_id: ID of the user

        Returns:
            List of questions
        """
        topic = f"{general_type}_{specific_type}"
        question_set = self.db_handler.get_question_set_by_topic_for_user(case_id, topic, user_id)
        
        validated_questions = []
        for question in question_set.questions:
            try:
                validated_question = QuestionRetrieve(
                    id=question.id,
                    question=question.question,
                    context=question.context,
                    difficulty=question.difficulty,
                    keywords=question.keywords,
                    general_type=question.general_type,
                    specific_type=question.specific_type,
                    answer=question.answer
                )
                validated_questions.append(validated_question)
            except Exception as e:
                print(f"Error validating question: {str(e)}")
                continue
        return validated_questions