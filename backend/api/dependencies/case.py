from fastapi import Depends
from typing import Annotated
from backend.services.case_service import CaseService
from backend.services.storage_service import StorageService
from backend.services.llm_service import LLMService
from backend.services.database_service import DatabaseService
from backend.handler.storage.file_converter import FileConverter
from backend.api.dependencies.storage import get_storage_service
from backend.api.dependencies.llm import get_llm_service
from backend.api.dependencies.database import get_database_service
from backend.api.dependencies.storage import get_file_converter


def get_case_service(
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
    llm_service: Annotated[LLMService, Depends(get_llm_service)],
    database_service: Annotated[DatabaseService, Depends(get_database_service)],
    file_converter: Annotated[FileConverter, Depends(get_file_converter)],
) -> CaseService:
    return CaseService(
        storage_service=storage_service,
        llm_service=llm_service,
        database_service=database_service,
        file_converter=file_converter,
    )


case_service_dependency = Annotated[CaseService, Depends(get_case_service)]
