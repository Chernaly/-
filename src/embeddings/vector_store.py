"""Vector store manager using ChromaDB."""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from ..core.config import get_config

logger = logging.getLogger(__name__)


class VectorStore:
    """Manages document embeddings in ChromaDB."""

    def __init__(self, persist_directory: str = None, collection_name: str = "documents"):
        """Initialize vector store.

        Args:
            persist_directory: Directory to persist ChromaDB
            collection_name: Name of the collection
        """
        if persist_directory is None:
            config = get_config()
            persist_directory = config.database.get('chroma', './data/vectors/chroma')

        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Lazy import to avoid loading ChromaDB until needed
        import chromadb
        from chromadb.config import Settings

        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        logger.info(f"Vector store initialized at {persist_directory}")

    def add_document(self, document_id: int, content: str, metadata: Dict = None):
        """Add a document to the vector store.

        Args:
            document_id: Document ID
            content: Document content
            metadata: Document metadata
        """
        try:
            # For now, use simple embedding (will be replaced with Claude embeddings)
            # ChromaDB will use its default embedding function if not specified
            self.collection.add(
                documents=[content],
                metadatas=[metadata or {}],
                ids=[str(document_id)]
            )

            logger.info(f"Added document {document_id} to vector store")

        except Exception as e:
            logger.error(f"Error adding document to vector store: {e}")
            raise

    def add_document_chunks(self, document_id: int, chunks: List[str],
                           metadata: Dict = None):
        """Add document chunks to vector store.

        Args:
            document_id: Document ID
            chunks: List of text chunks
            metadata: Document metadata
        """
        try:
            ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [{**(metadata or {}), 'chunk_index': i, 'document_id': document_id}
                        for i in range(len(chunks))]

            self.collection.add(
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(f"Added {len(chunks)} chunks for document {document_id}")

        except Exception as e:
            logger.error(f"Error adding document chunks: {e}")
            raise

    def search(self, query: str, n_results: int = 5,
              metadata_filter: Dict = None) -> List[Dict]:
        """Search for similar documents.

        Args:
            query: Search query
            n_results: Number of results to return
            metadata_filter: Metadata filters

        Returns:
            List of search results with 'id', 'document', 'metadata', 'distance'
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=metadata_filter
            )

            # Format results
            formatted_results = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        'id': results['ids'][0][i],
                        'document': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else None
                    })

            return formatted_results

        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []

    def delete_document(self, document_id: int):
        """Delete a document from the vector store.

        Args:
            document_id: Document ID
        """
        try:
            # Delete main document
            self.collection.delete(ids=[str(document_id)])

            # Delete chunks (if any)
            # Query for chunks with this document_id
            results = self.collection.get(
                where={"document_id": document_id}
            )

            if results['ids']:
                self.collection.delete(ids=results['ids'])

            logger.info(f"Deleted document {document_id} from vector store")

        except Exception as e:
            logger.error(f"Error deleting document: {e}")

    def update_document(self, document_id: int, content: str, metadata: Dict = None):
        """Update a document in the vector store.

        Args:
            document_id: Document ID
            content: New content
            metadata: New metadata
        """
        self.delete_document(document_id)
        self.add_document(document_id, content, metadata)

    def get_document_count(self) -> int:
        """Get total number of documents in store.

        Returns:
            Document count
        """
        return self.collection.count()

    def clear_collection(self):
        """Clear all documents from the collection."""
        # Get all IDs
        results = self.collection.get()
        if results['ids']:
            self.collection.delete(ids=results['ids'])
        logger.info("Cleared vector store collection")


# Global vector store instance
_vector_store = None


def get_vector_store(persist_directory: str = None) -> VectorStore:
    """Get global vector store instance.

    Args:
        persist_directory: Path to persist directory (only used on first call)

    Returns:
        VectorStore instance
    """
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore(persist_directory)
    return _vector_store
