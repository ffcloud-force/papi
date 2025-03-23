# test file upload_case_to_s3

from backend.modules.cases.case_handler import CaseHandler

def test_upload_case_to_s3():
    case_handler = CaseHandler()
    case_handler.upload_case_to_s3("", 1)
