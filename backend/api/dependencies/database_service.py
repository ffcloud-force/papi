from fastapi import Depends
from sqlalchemy.orm import Session
from backend.database.persistent.config import get_db
from backend.services.database_service import DatabaseService
from typing import Annotated

def get_database_service(db: Session = Depends(get_db)) -> DatabaseService:
    service = DatabaseService(db)
    return service

get_database_service_dependency = Annotated[DatabaseService, Depends(get_database_service)]
