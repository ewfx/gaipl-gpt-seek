from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
from typing import List, Dict, Optional
import uvicorn

from ..embeddings.document_processor import DocumentProcessor
from ..embeddings.vector_store import VectorStoreManager
from ..rag.complete_pipeline import IntegratedRAGSystem

app = FastAPI(title="Platform Support RAG API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
ARTIFACTS_DIR = "backend/vstore_artifacts"
DATA_DIR = "backend/incident_data"
os.makedirs(os.path.join(os.getcwd(),ARTIFACTS_DIR), exist_ok=True)
os.makedirs(os.path.join(os.getcwd(),DATA_DIR), exist_ok=True)

document_processor = DocumentProcessor()
vector_store = VectorStoreManager()

rag_system = IntegratedRAGSystem(
    use_cache=True,
    cache_ttl=3600,
    max_context_documents=4,
    context_window_size=2000
)


class QueryRequest(BaseModel):
    query: str
    additional_context: Optional[Dict] = None
    force_refresh: bool = False

class QueryResponse(BaseModel):
    response: str
    sources: List[Dict]

@app.post("/query")
async def query(
request: QueryRequest
):
    try:
        # Process through the complete integrated pipeline
        result = await rag_system.process_query(
            query=request.query,
            additional_context=request.additional_context,
            force_refresh=request.force_refresh
        )
        
        return result  # This will include both response and context information
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@app.post("/documents")
async def upload_document(file: UploadFile = File(...)):
    """Upload a new document to the knowledge base."""
    try:
        # Save the file
        file_path = os.path.join(DATA_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process and add to vector store
        documents = document_processor.load_documents(DATA_DIR)
        vector_store.add_documents(documents)
        
        # Save updated vector store
        vector_store.save(ARTIFACTS_DIR)

        return {"message": "Document uploaded and processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Check the health of the API."""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 