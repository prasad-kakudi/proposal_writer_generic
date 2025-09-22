import os
import PyPDF2
import docx
#from typing import str

class FileProcessor:
    """Service for processing uploaded files and extracting text content"""
    
    def __init__(self):
        self.supported_extensions = ['.pdf', '.txt', '.docx']
    
    def extract_text(self, filepath: str) -> str:
        """Extract text content from uploaded file based on its extension"""
        _, ext = os.path.splitext(filepath.lower())
        
        if ext == '.pdf':
            return self._extract_from_pdf(filepath)
        elif ext == '.txt':
            return self._extract_from_txt(filepath)
        elif ext == '.docx':
            return self._extract_from_docx(filepath)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    def _extract_from_pdf(self, filepath: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        
        return text.strip()
    
    def _extract_from_txt(self, filepath: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(filepath, 'r', encoding='latin-1') as file:
                return file.read().strip()
        except Exception as e:
            raise Exception(f"Error reading TXT file: {str(e)}")
    
    def _extract_from_docx(self, filepath: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(filepath)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading DOCX file: {str(e)}")
    
    def is_supported_file(self, filename: str) -> bool:
        """Check if file extension is supported"""
        _, ext = os.path.splitext(filename.lower())
        return ext in self.supported_extensions
