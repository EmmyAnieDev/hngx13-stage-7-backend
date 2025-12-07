# AI Document Summarization API

AI-powered document analysis service that accepts PDF/DOCX files, extracts text, and generates summaries with metadata using LLMs.

## Features

- Upload PDF and DOCX files (max 5MB)
- Extract text automatically
- AI-powered document summarization
- Document type detection (CV, invoice, report, letter, etc.)
- Metadata extraction based on document type
- MinIO/S3 storage support
- PostgreSQL database

## Quick Start with Docker Compose

### Prerequisites
- Docker and Docker Compose installed
- OpenRouter API key

### Setup

1. Clone the repository and navigate to project directory

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Edit `.env` and add your OpenRouter API key:
```env
OPENROUTER_API_KEY=your-actual-api-key-here
```

4. Start all services (app + postgres + minio):
```bash
docker-compose up --build
```

That's it! The API will be available at http://localhost:8000

**Services:**
- API: http://localhost:8000
- MinIO Console: http://localhost:9001 (login: minioadmin/minioadmin)
- Postgres: localhost:5432

### API Endpoints

1. **Upload Document**
```bash
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@your-document.pdf"
```

2. **Analyze Document**
```bash
curl -X POST http://localhost:8000/documents/{id}/analyze
```

3. **Get Document**
```bash
curl http://localhost:8000/documents/{id}
```

### Stop Services
```bash
docker-compose down
```

To remove all data (volumes):
```bash
docker-compose down -v
```

## Local Development (without Docker)

1. Install Python 3.12+

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL and MinIO locally, then update `.env`

5. Run the application:
```bash
uvicorn app.main:app --reload
```

## Tech Stack

- **FastAPI** - REST API framework
- **PostgreSQL** - Database
- **MinIO** - S3-compatible object storage
- **OpenRouter** - LLM API gateway
- **pypdf** - PDF text extraction
- **python-docx** - DOCX text extraction

## Environment Variables

See `.env.example` for all configuration options.

## License

MIT
