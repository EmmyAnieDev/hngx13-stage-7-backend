import os
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db, settings
from app.models import Document
from app.schemas import DocumentUploadResponse, DocumentAnalysisResponse, DocumentResponse
from app.services.document_service import DocumentService
from app.services.llm_service import LLMService

router = APIRouter(prefix="/documents", tags=["documents"])

# Ensure upload directory exists
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a PDF or DOCX file, extract text, and save to database."""

    # Validate file type
    allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    # Read file content
    content = await file.read()
    file_size = len(content)

    # Validate file size (5MB max)
    max_size = settings.max_file_size_mb * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(status_code=400, detail=f"File size exceeds {settings.max_file_size_mb}MB limit")

    # Save file to disk
    file_path = os.path.join(settings.upload_dir, f"{datetime.now().timestamp()}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(content)

    # Extract text
    try:
        extracted_text = DocumentService.extract_text(file_path, file.content_type)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

    # Save to database
    document = Document(
        filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        file_type=file.content_type,
        extracted_text=extracted_text
    )
    db.add(document)
    db.commit()
    db.refresh(document)

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

    # Analyze with LLM
    try:
        analysis = await LLMService.analyze_document(document.extracted_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    # Update document with analysis results
    document.summary = analysis["summary"]
    document.document_type = analysis["document_type"]
    document.metadata = analysis["metadata"]
    document.analyzed_at = datetime.now()

    db.commit()
    db.refresh(document)

    return DocumentAnalysisResponse(
        id=document.id,
        summary=document.summary,
        document_type=document.document_type,
        metadata=document.metadata,
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
        metadata=document.metadata,
        created_at=document.created_at,
        analyzed_at=document.analyzed_at
    )
