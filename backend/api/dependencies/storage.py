from fastapi import Depends
from backend.services.storage_service import StorageService
from backend.handler.storage.file_converter import FileConverter
from backend.handler.storage.storage_handler import StorageHandler
from typing import Annotated


def get_storage_handler() -> StorageHandler:
    return StorageHandler()


def get_storage_service(
    storage_handler: Annotated[StorageHandler, Depends(get_storage_handler)],
) -> StorageService:
    return StorageService(storage_handler)


def get_file_converter() -> FileConverter:
    return FileConverter()


storage_service_dependency = Annotated[StorageService, Depends(get_storage_service)]
file_converter_dependency = Annotated[FileConverter, Depends(get_file_converter)]
