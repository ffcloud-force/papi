from backend.services.database_service import DatabaseService

def get_database_service():
    db_service = DatabaseService()  # Creates service with business logic
    try:
        yield db_service           # Provides the service layer to the endpoint
    finally:
        db_service.db.close()     # Closes the underlying database session
