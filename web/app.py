"""Web application using FastAPI."""

import logging
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from fastapi import Request

from src.core.config import get_config
from src.core.database import get_db
from src.processors import create_processor
from src.search.search_engine import get_search_engine
from src.qa.answer_generator import get_answer_generator

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Knowledge Management System",
    description="AI-powered knowledge management with search and Q&A",
    version="1.0.0"
)

# Setup templates and static files
templates = Jinja2Templates(directory="web/templates")
app.mount("/static", StaticFiles(directory="web/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render home page."""
    db = get_db()
    documents = db.get_all_documents()[:10]  # Get latest 10 documents

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "documents": documents,
            "total_docs": len(db.get_all_documents())
        }
    )


@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request):
    """Render search page."""
    return templates.TemplateResponse("search.html", {"request": request})


@app.get("/api/documents")
async def list_documents(limit: int = 50, status: Optional[str] = None):
    """List all documents."""
    db = get_db()
    documents = db.get_all_documents(status=status)[:limit]

    return {
        "total": len(documents),
        "documents": [
            {
                "id": doc["id"],
                "title": doc["title"],
                "path": doc["path"],
                "summary": doc["summary"],
                "status": doc["processing_status"],
                "updated_at": doc["updated_at"]
            }
            for doc in documents
        ]
    }


@app.get("/api/documents/{document_id}")
async def get_document(document_id: int):
    """Get document details."""
    db = get_db()
    doc = db.get_document(document_id=document_id)

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    tags = db.get_document_tags(document_id)

    return {
        "document": doc,
        "tags": tags
    }


@app.post("/api/search")
async def search_documents(
    query: str = Form(...),
    method: str = Form("hybrid"),
    limit: int = Form(10),
    tags: Optional[str] = Form(None)
):
    """Search documents."""
    search_engine = get_search_engine()

    tag_list = tags.split(",") if tags else None

    results = search_engine.search(
        query=query,
        method=method,
        max_results=limit,
        tags=tag_list
    )

    return {
        "query": query,
        "method": method,
        "total": len(results),
        "results": results
    }


@app.post("/api/ask")
async def ask_question(question: str = Form(...), limit: int = Form(5)):
    """Answer a question."""
    answer_generator = get_answer_generator()

    result = answer_generator.answer_question(
        question=question,
        max_context=limit
    )

    return {
        "question": result["question"],
        "answer": result["answer"],
        "confidence": result["confidence"],
        "context_count": result["context_count"],
        "sources": [
            {
                "title": ctx["title"],
                "path": ctx.get("path", "")
            }
            for ctx in result["context"][:3]
        ]
    }


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a markdown document."""
    if not file.filename.endswith(('.md', '.markdown')):
        raise HTTPException(status_code=400, detail="Only markdown files are supported")

    # Save file
    config = get_config()
    watch_dir = Path(config.watcher.get('directories', ['./docs/watched'])[0])
    watch_dir.mkdir(parents=True, exist_ok=True)

    file_path = watch_dir / file.filename
    content = await file.read()

    with open(file_path, 'wb') as f:
        f.write(content)

    # Process document
    processor = create_processor(config)
    result = processor.process_document(str(file_path), event_type='upload')

    return {
        "filename": file.filename,
        "status": result["status"],
        "document_id": result.get("document_id"),
        "message": "Document uploaded and processed successfully"
    }


@app.get("/api/stats")
async def get_statistics():
    """Get system statistics."""
    db = get_db()
    documents = db.get_all_documents()

    stats = {
        "total_documents": len(documents),
        "completed": sum(1 for d in documents if d["processing_status"] == "completed"),
        "pending": sum(1 for d in documents if d["processing_status"] == "pending"),
        "failed": sum(1 for d in documents if d["processing_status"] == "failed")
    }

    return stats


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Knowledge Management System"}


def start_web_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the web server."""
    import uvicorn

    print(f"\n🌐 Starting web server at http://{host}:{port}")
    print(f"📚 API documentation: http://{host}:{port}/docs")
    print(f"📖 ReDoc documentation: http://{host}:{port}/redoc\n")

    uvicorn.run(
        "web.app:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    start_web_server()
