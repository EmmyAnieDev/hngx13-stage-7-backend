import logging
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db, settings
from app.models import Document
from app.schemas import DocumentUploadResponse, DocumentAnalysisResponse, DocumentResponse
from app.services.document_service import DocumentService
from app.services.llm_service import LLMService
from app.services.storage_service import StorageService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a PDF or DOCX file, extract text, and save to database."""

    allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    content = await file.read()
    file_size = len(content)

    max_size = settings.max_file_size_mb * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(status_code=400, detail=f"File size exceeds {settings.max_file_size_mb}MB limit")

    object_name = f"{datetime.now().timestamp()}_{file.filename}"

    try:
        StorageService.upload_file(content, object_name)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to upload file {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save uploaded file")

    try:
        extracted_text = DocumentService.extract_text_from_bytes(content, file.content_type)
    except ValueError as e:
        StorageService.delete_file(object_name)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error extracting text from {file.filename}: {str(e)}")
        StorageService.delete_file(object_name)
        raise HTTPException(status_code=500, detail="Failed to process document")

    try:
        document = Document(
            filename=file.filename,
            file_path=object_name,
            file_size=file_size,
            file_type=file.content_type,
            extracted_text=extracted_text
        )
        db.add(document)
        db.commit()
        db.refresh(document)
    except Exception as e:
        logger.error(f"Database error saving document {file.filename}: {str(e)}")
        StorageService.delete_file(object_name)
        raise HTTPException(status_code=500, detail="Failed to save document information")

    return DocumentUploadResponse(
        id=document.id,
        filename=document.filename,
        file_size=document.file_size,
        file_type=document.file_type,
        created_at=document.created_at,
        message="Document uploaded and text extracted successfully"
    )


@router.post("/{document_id}/analyze", response_model=DocumentAnalysisResponse)
async def analyze_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Analyze document using LLM and extract metadata."""

    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if not document.extracted_text:
        raise HTTPException(status_code=400, detail="No extracted text available")

    try:
        analysis = await LLMService.analyze_document(document.extracted_text)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error analyzing document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Document analysis failed")

    try:
        document.summary = analysis["summary"]
        document.document_type = analysis["document_type"]
        document.extracted_metadata = analysis["metadata"]
        document.analyzed_at = datetime.now()

        db.commit()
        db.refresh(document)
    except Exception as e:
        logger.error(f"Database error saving analysis for document {document_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to save analysis results")

    return DocumentAnalysisResponse(
        id=document.id,
        summary=document.summary,
        document_type=document.document_type,
        metadata=document.extracted_metadata,
        analyzed_at=document.analyzed_at
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get complete document information including analysis results."""

    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentResponse(
        id=document.id,
        filename=document.filename,
        file_size=document.file_size,
        file_type=document.file_type,
        extracted_text=document.extracted_text,
        summary=document.summary,
        document_type=document.document_type,
        metadata=document.extracted_metadata,
        created_at=document.created_at,
        analyzed_at=document.analyzed_at
    )