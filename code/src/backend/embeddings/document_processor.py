from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
import os

class DocumentProcessor:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: List[str] = ["\n\n", "\n", " ", ""],
        length_function: callable = len,
        enable_markdown: bool = False
    ):
        """Initialize the document processor.
        
        Args:
            chunk_size (int): The size of text chunks (in characters)
            chunk_overlap (int): The overlap between chunks (in characters)
            separators (List[str]): List of separators to use for text splitting
            length_function (callable): Function to measure text length
            enable_markdown (bool): Whether to process markdown files
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.enable_markdown = enable_markdown
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=length_function,
            separators=separators
        )

    def load_documents(self, directory_path: str, glob_pattern: str = "**/*.*") -> List[Dict]:
        """Load documents from a directory.
        
        Args:
            directory_path (str): Path to the directory containing documents
            glob_pattern (str): Pattern to match files (e.g., "*.txt" for text files only)
        """
        loader = DirectoryLoader(
            directory_path,
            glob=glob_pattern,
            loader_cls=TextLoader,
            show_progress=True
        )
        documents = loader.load()
        return self._process_documents(documents)

    def _process_documents(self, documents: List) -> List[Dict]:
        """Process and chunk documents."""
        processed_docs = []
        
        for doc in documents:
            content = doc.page_content
            metadata = doc.metadata.copy()
            
            # Convert markdown to plain text if needed
            if (self.enable_markdown and 
                metadata.get("source", "").endswith((".md", ".markdown"))):
                content = self._convert_markdown_to_text(content)
            
            # Split into chunks
            chunks = self.text_splitter.split_text(content)
            
            # Create processed documents with metadata
            for i, chunk in enumerate(chunks):
                doc_dict = {
                    "content": chunk,
                    "metadata": {
                        "chunk_index": i,
                        "source": os.path.basename(metadata.get("source", "")),
                        "chunk_size": self.chunk_size,
                        "chunk_overlap": self.chunk_overlap,
                        "total_chunks": len(chunks)
                    }
                }
                processed_docs.append(doc_dict)
        
        return processed_docs