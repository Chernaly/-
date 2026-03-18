"""Unified search engine combining keyword and semantic search."""

import logging
from typing import Dict, List, Optional

from ..core.config import get_config
from ..core.database import get_db
from ..embeddings.vector_store import get_vector_store

logger = logging.getLogger(__name__)


class SearchEngine:
    """Provides hybrid search capabilities."""

    def __init__(self, use_vectors: bool = True):
        """Initialize search engine.

        Args:
            use_vectors: Whether to use vector search
        """
        self.db = get_db()
        self.use_vectors = use_vectors
        self.vector_store = get_vector_store() if use_vectors else None
        self.config = get_config()

    def search(self, query: str, method: str = 'hybrid',
              max_results: int = None, tags: List[str] = None) -> List[Dict]:
        """Search documents.

        Args:
            query: Search query
            method: Search method ('keyword', 'semantic', 'hybrid')
            max_results: Maximum number of results
            tags: Filter by tags

        Returns:
            List of search results
        """
        max_results = max_results or self.config.search.get('max_results', 20)

        if method == 'keyword':
            results = self._keyword_search(query, max_results, tags)
        elif method == 'semantic':
            results = self._semantic_search(query, max_results, tags)
        elif method == 'hybrid':
            results = self._hybrid_search(query, max_results, tags)
        else:
            logger.warning(f"Unknown search method: {method}, using hybrid")
            results = self._hybrid_search(query, max_results, tags)

        return results

    def _keyword_search(self, query: str, max_results: int,
                       tags: List[str] = None) -> List[Dict]:
        """Perform keyword-based search.

        Args:
            query: Search query
            max_results: Maximum results
            tags: Filter by tags

        Returns:
            List of results
        """
        # Simple keyword search using LIKE
        # In production, would use SQLite FTS5
        import sqlite3

        conn = self.db._get_connection()
        cursor = conn.cursor()

        sql = """
            SELECT DISTINCT d.*, GROUP_CONCAT(t.name) as tags
            FROM documents d
            LEFT JOIN document_tags dt ON d.id = dt.document_id
            LEFT JOIN tags t ON dt.tag_id = t.id
            WHERE (d.title LIKE ? OR d.summary LIKE ?)
        """

        params = [f"%{query}%", f"%{query}%"]

        if tags:
            placeholders = ','.join('?' * len(tags))
            sql += f"""
                AND d.id IN (
                    SELECT document_id FROM document_tags dt
                    JOIN tags t ON dt.tag_id = t.id
                    WHERE t.name IN ({placeholders})
                )
            """
            params.extend(tags)

        sql += " GROUP BY d.id ORDER BY d.updated_at DESC LIMIT ?"
        params.append(max_results)

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            result = dict(row)
            result['score'] = 1.0  # Basic scoring
            result['search_method'] = 'keyword'
            results.append(result)

        return results

    def _semantic_search(self, query: str, max_results: int,
                        tags: List[str] = None) -> List[Dict]:
        """Perform semantic search using vectors.

        Args:
            query: Search query
            max_results: Maximum results
            tags: Filter by tags

        Returns:
            List of results
        """
        if not self.vector_store:
            logger.warning("Vector store not available, falling back to keyword search")
            return self._keyword_search(query, max_results, tags)

        # Search vector store
        metadata_filter = None
        if tags:
            # ChromaDB metadata filtering
            metadata_filter = {"tags": {"$in": tags}}

        vector_results = self.vector_store.search(
            query=query,
            n_results=max_results,
            metadata_filter=metadata_filter
        )

        # Fetch full document data
        results = []
        for vr in vector_results:
            doc_id = int(vr['id'].split('_')[0])  # Handle chunked documents
            doc = self.db.get_document(document_id=doc_id)

            if doc:
                doc['score'] = 1 - vr['distance'] if vr['distance'] else 1.0
                doc['search_method'] = 'semantic'
                doc['chunk'] = vr['document']
                results.append(doc)

        return results

    def _hybrid_search(self, query: str, max_results: int,
                      tags: List[str] = None) -> List[Dict]:
        """Perform hybrid search combining keyword and semantic.

        Args:
            query: Search query
            max_results: Maximum results
            tags: Filter by tags

        Returns:
            List of results
        """
        # Get results from both methods
        keyword_results = self._keyword_search(query, max_results, tags)
        semantic_results = self._semantic_search(query, max_results, tags)

        # Combine and deduplicate
        combined = {}
        keyword_weight = 0.4
        semantic_weight = 0.6

        for result in keyword_results:
            doc_id = result['id']
            combined[doc_id] = result
            combined[doc_id]['score'] = result['score'] * keyword_weight

        for result in semantic_results:
            doc_id = result['id']
            if doc_id in combined:
                combined[doc_id]['score'] += result['score'] * semantic_weight
                combined[doc_id]['search_method'] = 'hybrid'
            else:
                combined[doc_id] = result
                combined[doc_id]['score'] = result['score'] * semantic_weight
                combined[doc_id]['search_method'] = 'hybrid'

        # Sort by combined score
        results = sorted(combined.values(), key=lambda x: x['score'], reverse=True)

        return results[:max_results]

    def search_by_tags(self, tags: List[str], max_results: int = None) -> List[Dict]:
        """Search documents by tags.

        Args:
            tags: List of tags to search
            max_results: Maximum results

        Returns:
            List of results
        """
        max_results = max_results or self.config.search.get('max_results', 20)

        import sqlite3

        conn = self.db._get_connection()
        cursor = conn.cursor()

        placeholders = ','.join('?' * len(tags))
        sql = f"""
            SELECT d.*, GROUP_CONCAT(t.name) as matched_tags
            FROM documents d
            JOIN document_tags dt ON d.id = dt.document_id
            JOIN tags t ON dt.tag_id = t.id
            WHERE t.name IN ({placeholders})
            GROUP BY d.id
            ORDER BY COUNT(DISTINCT t.id) DESC, d.updated_at DESC
            LIMIT ?
        """

        cursor.execute(sql, tags + [max_results])
        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            result = dict(row)
            result['search_method'] = 'tags'
            results.append(result)

        return results

    def get_similar_documents(self, document_id: int, max_results: int = 5) -> List[Dict]:
        """Find similar documents.

        Args:
            document_id: Document ID
            max_results: Maximum results

        Returns:
            List of similar documents
        """
        doc = self.db.get_document(document_id)
        if not doc:
            return []

        # Use semantic search on document content/summary
        query = doc.get('summary') or doc.get('title', '')
        results = self._semantic_search(query, max_results + 1)  # +1 to exclude self

        # Filter out the original document
        return [r for r in results if r['id'] != document_id][:max_results]


# Global search engine instance
_search_engine = None


def get_search_engine(use_vectors: bool = True) -> SearchEngine:
    """Get global search engine instance.

    Args:
        use_vectors: Whether to use vector search

    Returns:
        SearchEngine instance
    """
    global _search_engine
    if _search_engine is None:
        _search_engine = SearchEngine(use_vectors)
    return _search_engine
