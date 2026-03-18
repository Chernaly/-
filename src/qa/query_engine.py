"""Query engine for processing user questions."""

import logging
from typing import Dict, List

from ..core.config import get_config
from ..core.database import get_db
from ..search.search_engine import get_search_engine

logger = logging.getLogger(__name__)


class QueryEngine:
    """Processes natural language queries."""

    def __init__(self):
        """Initialize query engine."""
        self.db = get_db()
        self.search_engine = get_search_engine()
        self.config = get_config()

    def process_query(self, question: str, max_context: int = 5) -> Dict:
        """Process a natural language query.

        Args:
            question: User question
            max_context: Maximum context documents

        Returns:
            Query result with context and answer
        """
        # Extract keywords from question
        keywords = self._extract_keywords(question)

        # Search for relevant documents
        search_results = self.search_engine.search(
            query=' '.join(keywords),
            method='hybrid',
            max_results=max_context
        )

        # Prepare context
        context = []
        for result in search_results:
            doc_data = {
                'id': result['id'],
                'title': result.get('title', 'Untitled'),
                'path': result.get('path', ''),
                'summary': result.get('summary', ''),
                'content': result.get('chunk', ''),  # Use chunk if available
                'tags': result.get('tags', '').split(',') if result.get('tags') else [],
                'score': result.get('score', 0)
            }
            context.append(doc_data)

        return {
            'question': question,
            'keywords': keywords,
            'context': context,
            'context_count': len(context)
        }

    def _extract_keywords(self, question: str) -> List[str]:
        """Extract keywords from a question.

        Args:
            question: User question

        Returns:
            List of keywords
        """
        # Simple keyword extraction
        # Remove common words
        stop_words = {'what', 'how', 'why', 'when', 'where', 'which', 'who',
                     'is', 'are', 'was', 'were', 'be', 'been', 'being',
                     'have', 'has', 'had', 'do', 'does', 'did',
                     'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to'}

        words = question.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 2]

        return keywords

    def get_document_context(self, document_id: int) -> Dict:
        """Get context for a specific document.

        Args:
            document_id: Document ID

        Returns:
            Document context dictionary
        """
        doc = self.db.get_document(document_id)
        if not doc:
            return {}

        # Get related documents
        similar = self.search_engine.get_similar_documents(document_id)

        return {
            'document': doc,
            'similar_documents': similar
        }


# Global query engine instance
_query_engine = None


def get_query_engine() -> QueryEngine:
    """Get global query engine instance.

    Returns:
        QueryEngine instance
    """
    global _query_engine
    if _query_engine is None:
        _query_engine = QueryEngine()
    return _query_engine
