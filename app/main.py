from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import documents

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Document Analysis API",
    description="Upload documents and get AI-powered summaries and metadata extraction",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router)


@app.get("/")
async def root():
    return {
        "message": "Document Analysis API",
        "endpoints": {
            "upload": "POST /documents/upload",
            "analyze": "POST /documents/{id}/analyze",
            "get": "GET /documents/{id}"
        }
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
