import PyPDF2
import io
import os


class PDFParser:
    """Utility class for parsing PDF files to extract text content"""

    def __init__(self):
        self.supported_formats = [".pdf"]

    def extract_text_from_pdf(self, file_path):
        """Extract text content from a PDF file"""
        try:
            if not os.path.exists(file_path):
                return "File not found"

            text = ""
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)

                # Extract text from all pages
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"

            return text.strip()

        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return f"Error reading PDF: {str(e)}"

    def extract_text_from_file_object(self, file_object):
        """Extract text from a file object (uploaded file)"""
        try:
            text = ""
            file_object.seek(0)  # Reset file pointer

            pdf_reader = PyPDF2.PdfReader(file_object)

            # Extract text from all pages
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"

            return text.strip()

        except Exception as e:
            print(f"Error extracting text from file object: {e}")
            return f"Error reading PDF: {str(e)}"

    def is_pdf_file(self, filename):
        """Check if the file is a PDF based on its extension"""
        return filename.lower().endswith(".pdf")

    def validate_pdf(self, file_path):
        """Validate if the PDF file is readable"""
        try:
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                # Try to read the first page
                if len(pdf_reader.pages) > 0:
                    pdf_reader.pages[0].extract_text()
                return True
        except Exception as e:
            print(f"PDF validation error: {e}")
            return False
