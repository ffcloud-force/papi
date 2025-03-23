from PyPDF2 import PdfReader

class FileConverter:
    def __init__(self):
        # Don't initialize PdfReader here, as it needs a file stream
        pass

    def convert_pdf_to_text(self, file_path: str):
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
    
    # @TODO: add other file types

if __name__ == "__main__":
    converter = FileConverter()
    print(converter.convert_pdf_to_text("backend/data/example_cases/case1.pdf"))