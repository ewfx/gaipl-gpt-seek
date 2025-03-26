from typing import List, Dict
import faiss
import numpy as np
import pickle
import os
from langchain_community.embeddings import OllamaEmbeddings

class VectorStoreManager:
    def __init__(self, model_name: str = "mistral", dimension: int = 4096):
        self.embeddings = OllamaEmbeddings(model=model_name)
        self.dimension = dimension
        self.index = None
        self.documents = []

    def add_documents(self, documents: List[Dict]):
        """Add documents to the vector store."""
        texts = [doc["content"] for doc in documents]
        embeddings = self.embeddings.embed_documents(texts)
        
        if self.index is None:
            self.index = faiss.IndexFlatL2(self.dimension)
        
        # Convert embeddings to numpy array and add to FAISS
        embeddings_array = np.array(embeddings).astype('float32')
        self.index.add(embeddings_array)
        
        # Store documents
        self.documents.extend(documents)

    def similarity_search(self, query: str, k: int = 4) -> List[Dict]:
        """Perform similarity search for a query."""
        if self.index is None or not self.documents:
            return []

        # Get query embedding
        query_embedding = self.embeddings.embed_query(query)
        query_embedding_array = np.array([query_embedding]).astype('float32')

        # Perform similarity search
        distances, indices = self.index.search(query_embedding_array, k)
        
        # Return relevant documents
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):  # Ensure index is valid
                doc = self.documents[idx].copy()
                
                # Convert L2 distance to cosine similarity-like score
                # FAISS returns squared L2 distance, so we need to:
                # 1. Take the square root to get L2 distance
                # 2. Convert to a similarity score between 0 and 1
                l2_distance = np.sqrt(float(distances[0][i]))
                
                # Convert distance to similarity score
                # Using a scaled exponential decay function
                # This gives us a score that:
                # - Is 1.0 for perfect matches (distance = 0)
                # - Decays exponentially as distance increases
                # - Is always between 0 and 1
                similarity_score = np.exp(-l2_distance / self.dimension)
                
                doc["score"] = round(float(similarity_score), 4)
                results.append(doc)
        
        # Sort by score in descending order
        return sorted(results, key=lambda x: x["score"], reverse=True)

    def save(self, directory: str):
        """Save the vector store and documents to disk."""
        os.makedirs(directory, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, os.path.join(directory, "index.faiss"))
        
        # Save documents
        with open(os.path.join(directory, "documents.pkl"), "wb") as f:
            pickle.dump(self.documents, f)

    def load(self, directory: str):
        """Load the vector store and documents from disk."""
        # Load FAISS index
        self.index = faiss.read_index(os.path.join(os.getcwd(),directory, "index.faiss"))
        # print(os.path.join(os.getcwd(),directory))
        # Load documents
        with open(os.path.join(os.getcwd(),directory, "documents.pkl"), "rb") as f:
            self.documents = pickle.load(f) 
        # print(self.documents)