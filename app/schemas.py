from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID


class DocumentUploadResponse(BaseModel):
    id: UUID
    filename: str
    file_size: int
    file_type: str
    created_at: datetime
    message: str

    class Config:
        from_attributes = True


class DocumentAnalysisResponse(BaseModel):
    id: UUID
    summary: str
    document_type: str
    metadata: Dict[str, Any]
    analyzed_at: datetime

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    file_size: int
    file_type: str
    extracted_text: Optional[str] = None
    summary: Optional[str] = None
    document_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    analyzed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
