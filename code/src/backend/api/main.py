from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from typing import List, Dict, Optional
import uvicorn

from ..embeddings.document_processor import DocumentProcessor
from ..embeddings.vector_store import VectorStoreManager
from ..rag.complete_pipeline import IntegratedRAGSystem
from ..utils.constants import ARTIFACTS_DIR, DATA_DIR
from ..utils.pydantic_classes import QueryRequest, QueryResponse, ExecuteCommandRequest

app = FastAPI(title="Platform Support RAG API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.post("/execute", tags=["Commands"])
async def execute_command(request: ExecuteCommandRequest):
    try:
        return {
            "status": "success",
            "output": "Command executed successfully\nOutput: Mock command output",
            "splunk_link": f"https://splunk.example.com/search?q=search%20command%3D{request.command}"
        }
    except Exception as e:
        return {
            "status": "error",
            "output": f"Error executing command: {str(e)}",
            "splunk_link": ""
        }

@app.get("/")
async def root():
    return {
        "name": "Incident Resolution Gen-AI powered Platform",
        "version": "0.1.0",
        "status": "operational"
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 