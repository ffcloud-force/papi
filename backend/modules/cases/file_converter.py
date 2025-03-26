from PyPDF2 import PdfReader
from io import BytesIO

class FileConverter:
    def __init__(self):
        # Don't initialize PdfReader here, as it needs a file stream
        pass

    def convert_file_to_text(self, file_path: str):
        """
        Convert a file to text
        """
        if file_path.endswith(".pdf"):
            return self._convert_pdf_to_text(file_path)
        else:
            raise ValueError("Only PDF files are currently supported")

    def _convert_pdf_to_text(self, file_path: str):
        """
        Convert a PDF file to text
        """
        # Create the PdfReader with the file path directly
        # Opening file directly with the path instead of closing the file handle
        reader = PdfReader(file_path)
        
        # Extract text from all pages
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        return text
    
    def convert_pdf_from_bytes(self, pdf_bytes):
        """
        Extract text from PDF binary data
        """
        # Using libraries like PyPDF2 or pdfplumber to process binary data
        # Example with PyPDF2:
        
        reader = PdfReader(BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        return text
    
    # @TODO: add other file types

if __name__ == "__main__":
    converter = FileConverter()
    print(converter.convert_pdf_to_text("backend/data/example_cases/case1.pdf"))