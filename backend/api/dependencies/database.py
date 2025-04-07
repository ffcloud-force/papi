from fastapi import Depends
from sqlalchemy.orm import Session
from backend.database.persistent.config import get_db
from backend.services.database_service import DatabaseService
from backend.handler.database.database_handler import DatabaseHandler
from typing import Annotated

def get_database_handler(db: Session = Depends(get_db)) -> DatabaseHandler:
    return DatabaseHandler(db)

def get_database_service(
    db_handler: Annotated[DatabaseHandler, Depends(get_database_handler)]
) -> DatabaseService:
    return DatabaseService(db_handler)

get_database_handler_dependency = Annotated[DatabaseHandler, Depends(get_database_handler)]
get_database_service_dependency = Annotated[DatabaseService, Depends(get_database_service)]
