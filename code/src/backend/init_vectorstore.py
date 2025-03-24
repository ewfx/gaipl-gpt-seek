from embeddings.document_processor import DocumentProcessor
from embeddings.vector_store import VectorStoreManager
import os

def init_vectorstore(chunk_size: int = 1500, chunk_overlap: int = 200):
    """Initialize vector store with configurable chunk sizes.
    
    For IT incident data, recommended chunk sizes:
    - 1500 characters: Typically keeps one full incident together
      (Description ~300 chars + Resolution ~400 chars + KB link ~100 chars + formatting)
    - 200 characters overlap: Ensures context is maintained between incidents
    
    Rationale:
    1. Keep each incident as a complete unit when possible
    2. Maintain context between related incidents
    3. Allow enough overlap to catch similar issues
    4. Balance between context and specificity
    
    Args:
        chunk_size (int): Size of text chunks in characters
        chunk_overlap (int): Overlap between chunks in characters
    """
    print(f"Initializing vector store with chunk_size={chunk_size}, overlap={chunk_overlap}...")
    
    # Initialize components with incident-optimized chunking
    doc_processor = DocumentProcessor(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        # Prioritize splitting at incident boundaries
        separators=["\n\nIncident", "\n\nDescription:", "\n\n", "\n", " ", ""]
    )
    vector_store = VectorStoreManager()
    
    # Process documents
    data_dir = os.path.join("incident_data")
    print(f"Loading documents from {data_dir}...")
    documents = doc_processor.load_documents(data_dir, glob_pattern="*.txt")
    print(f"Found {len(documents)} document chunks")
    
    # Add to vector store
    print("Adding documents to vector store...")
    vector_store.add_documents(documents)
    
    # Save vector store
    artifacts_dir = "vstore_artifacts"
    os.makedirs(artifacts_dir, exist_ok=True)
    print(f"Saving vector store to {artifacts_dir}...")
    vector_store.save(artifacts_dir)
    print("Vector store initialized successfully!")

if __name__ == "__main__":
    # Use chunk size that keeps each incident as a complete unit
    init_vectorstore(chunk_size=1500, chunk_overlap=200) 