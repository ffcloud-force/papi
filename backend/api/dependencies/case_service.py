from backend.services.case_service import CaseService

def get_case_service() -> CaseService:
    return CaseService()