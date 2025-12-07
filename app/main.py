import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import documents

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Document Analysis API",
    description="Upload documents and get AI-powered summaries and metadata extraction",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.on_event("startup")
async def startup_event():
    logger.info("Document Analysis API started")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Document Analysis API shutting down")