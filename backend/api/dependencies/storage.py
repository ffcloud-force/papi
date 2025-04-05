from fastapi import Depends
from backend.services.storage_service import StorageService
from backend.handler.storage.file_converter import FileConverter
from typing import Annotated

def get_storage_service() -> StorageService:
    return StorageService()

def get_file_converter() -> FileConverter:
    return FileConverter()

get_storage_service_dependency = Annotated[StorageService, Depends(get_storage_service)]
get_file_converter_dependency = Annotated[FileConverter, Depends(get_file_converter)]
