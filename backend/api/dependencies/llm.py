from fastapi import Depends
from typing import Annotated
from backend.services.llm_service import LLMService
from backend.services.database_service import DatabaseService
from backend.handler.llm.llm_handler import LLMHandler
from backend.handler.storage.file_converter import FileConverter
from backend.api.dependencies.database import get_database_service
from backend.api.dependencies.storage import get_file_converter
from backend.handler.llm.providers.openai_singleton import get_openai_client


def get_llm_handler() -> LLMHandler:
    openai_client = get_openai_client()
    return LLMHandler(openai_client)


def get_llm_service(
    llm_handler: Annotated[LLMHandler, Depends(get_llm_handler)],
    database_service: Annotated[DatabaseService, Depends(get_database_service)],
    file_converter: Annotated[FileConverter, Depends(get_file_converter)],
) -> LLMService:
    return LLMService(
        llm_handler=llm_handler,
        db_service=database_service,
        file_converter=file_converter,
    )


# Create annotated dependencies for type hints
llm_handler_dependency = Annotated[LLMHandler, Depends(get_llm_handler)]
llm_service_dependency = Annotated[LLMService, Depends(get_llm_service)]
