# Document Analysis API

AI-powered document summarization and metadata extraction service built with FastAPI and OpenRouter.

## Features

- Upload PDF and DOCX files (max 5MB)
- Automatic text extraction
- LLM-powered document analysis
- Extract metadata (dates, amounts, names, etc.)
- Detect document type (invoice, CV, report, letter, etc.)
- RESTful API

## Tech Stack

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database
- **OpenRouter** - LLM API gateway
- **pypdf** - PDF text extraction
- **python-docx** - DOCX text extraction

## Quick Start

### 1. Prerequisites

- Python 3.9+
- Docker & Docker Compose
- OpenRouter API key ([get one here](https://openrouter.ai/))

### 2. Setup

Clone and navigate to the project:

```bash
cd hngx13-stage-7-backend
```

Create environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenRouter API key:

```
DATABASE_URL=postgresql://user:password@localhost:5432/documents_db
OPENROUTER_API_KEY=your_actual_api_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=5
```

Start PostgreSQL:

```bash
docker-compose up -d
```

Install Python dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the API

```bash
uvicorn app.main:app --reload
```

API will be available at: `http://localhost:8000`

Interactive docs at: `http://localhost:8000/docs`

## API Endpoints

### 1. Upload Document

```bash
POST /documents/upload
```

Upload a PDF or DOCX file.

**Example:**

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@invoice.pdf"
```

**Response:**

```json
{
  "id": 1,
  "filename": "invoice.pdf",
  "file_size": 245678,
  "file_type": "application/pdf",
  "created_at": "2025-12-06T10:30:00Z",
  "message": "Document uploaded and text extracted successfully"
}
```

### 2. Analyze Document

```bash
POST /documents/{id}/analyze
```

Send document text to LLM for analysis.

**Example:**

```bash
curl -X POST "http://localhost:8000/documents/1/analyze"
```

**Response:**

```json
{
  "id": 1,
  "summary": "Invoice from Acme Corp for software development services totaling $5,000.",
  "document_type": "invoice",
  "metadata": {
    "date": "2025-11-30",
    "invoice_number": "INV-2025-001",
    "total_amount": "$5,000",
    "vendor": "Acme Corp",
    "client": "Tech Solutions Inc"
  },
  "analyzed_at": "2025-12-06T10:31:00Z"
}
```

### 3. Get Document

```bash
GET /documents/{id}
```

Retrieve complete document information.

**Example:**

```bash
curl "http://localhost:8000/documents/1"
```

**Response:**

```json
{
  "id": 1,
  "filename": "invoice.pdf",
  "file_size": 245678,
  "file_type": "application/pdf",
  "extracted_text": "INVOICE\nAcme Corp...",
  "summary": "Invoice from Acme Corp...",
  "document_type": "invoice",
  "metadata": {
    "date": "2025-11-30",
    "invoice_number": "INV-2025-001",
    "total_amount": "$5,000"
  },
  "created_at": "2025-12-06T10:30:00Z",
  "analyzed_at": "2025-12-06T10:31:00Z"
}
```

## Testing

Using the interactive docs:

1. Go to `http://localhost:8000/docs`
2. Click "Try it out" on any endpoint
3. Upload a document and test the workflow

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database config & settings
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── routers/
│   │   └── documents.py     # Document endpoints
│   └── services/
│       ├── document_service.py  # Text extraction
│       └── llm_service.py       # LLM integration
├── uploads/                 # Uploaded files
├── requirements.txt
├── docker-compose.yml
└── .env
```

## Document Types Supported

The LLM can detect:

- **Invoice** - extracts vendor, client, amount, invoice number, date
- **CV/Resume** - extracts name, contact, skills, experience
- **Report** - extracts title, author, date, department
- **Letter** - extracts sender, recipient, date, subject
- **Contract** - extracts parties, date, contract type, value

## Configuration

Edit `.env` to configure:

- `DATABASE_URL` - PostgreSQL connection string
- `OPENROUTER_API_KEY` - Your OpenRouter API key
- `OPENROUTER_MODEL` - LLM model to use (default: gpt-4o-mini)
- `UPLOAD_DIR` - Where to store uploaded files
- `MAX_FILE_SIZE_MB` - Maximum file size in MB

## Production Deployment

For production:

1. Use a proper secrets manager for API keys
2. Set up file storage on S3/MinIO instead of local filesystem
3. Add authentication and rate limiting
4. Configure proper CORS origins
5. Use a production database with backups
6. Set up monitoring and logging

## Troubleshooting

**Database connection error:**
- Ensure PostgreSQL is running: `docker-compose ps`
- Check DATABASE_URL in `.env`

**OpenRouter API error:**
- Verify your API key is correct
- Check you have credits at openrouter.ai

**File upload fails:**
- Check file is PDF or DOCX
- Ensure file is under 5MB
- Verify `uploads/` directory has write permissions

## License

MIT
