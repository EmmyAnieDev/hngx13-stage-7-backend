import logging
from io import BytesIO
from pypdf import PdfReader
from docx import Document as DocxDocument

logger = logging.getLogger(__name__)


class DocumentService:
    @staticmethod
    def extract_text_from_pdf_bytes(content: bytes) -> str:
        """Extract text from PDF bytes."""
        try:
            reader = PdfReader(BytesIO(content))
            text = []
            for page in reader.pages:
                text.append(page.extract_text())
            return "\n\n".join(text)
        except Exception as e:
            logger.error(f"PDF extraction failed: {str(e)}")
            raise ValueError("Failed to extract text from PDF file")

    @staticmethod
    def extract_text_from_docx_bytes(content: bytes) -> str:
        """Extract text from DOCX bytes."""
        try:
            doc = DocxDocument(BytesIO(content))
            text = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text.append(paragraph.text)
            return "\n\n".join(text)
        except Exception as e:
            logger.error(f"DOCX extraction failed: {str(e)}")
            raise ValueError("Failed to extract text from DOCX file")

    @staticmethod
    def extract_text_from_bytes(content: bytes, file_type: str) -> str:
        """Extract text from file bytes based on file type."""
        if file_type == "application/pdf":
            return DocumentService.extract_text_from_pdf_bytes(content)
        elif file_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
            return DocumentService.extract_text_from_docx_bytes(content)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")