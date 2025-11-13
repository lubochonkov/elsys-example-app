# File Storage API

A simple FastAPI server for storing and retrieving files.

## Installation

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

Start the server with:
```bash
uvicorn main:app --reload
```

The server will start on `http://localhost:8000`

## API Endpoints

### GET `/files/{filename}`
Retrieve a file by filename.

**Example:**
```bash
curl http://localhost:8000/files/myfile.txt
```

### POST `/files`
Store a file locally on the filesystem.

**Example:**
```bash
curl -X POST -F "file=@/path/to/your/file.txt" http://localhost:8000/files
```

### GET `/files`
List all stored files.

**Example:**
```bash
curl http://localhost:8000/files
```

### GET `/health`
Health check endpoint to verify server status.

**Example:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000000",
  "service": "File Storage API"
}
```

### GET `/metrics`
Metrics endpoint providing server statistics including file counter and storage usage.

**Example:**
```bash
curl http://localhost:8000/metrics
```

**Response:**
```json
{
  "files_stored_total": 10,
  "files_current": 8,
  "total_storage_bytes": 1048576,
  "total_storage_mb": 1.0,
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

## API Documentation

Once the server is running, you can access:
- Interactive API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc

## Storage

Files are stored in the `storage/` directory, which is created automatically when the server starts.

