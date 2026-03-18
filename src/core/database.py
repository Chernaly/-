"""Database management for knowledge management system."""

import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .config import get_config


class Database:
    """SQLite database manager for document metadata and relationships."""

    def __init__(self, db_path: str = None):
        """Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        if db_path is None:
            config = get_config()
            db_path = config.database.get('sqlite', './data/db/knowledge.db')

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory.

        Returns:
            SQLite connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_schema(self):
        """Initialize database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                title TEXT,
                summary TEXT,
                content_hash TEXT,
                file_size INTEGER,
                word_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_processed TIMESTAMP,
                processing_status TEXT DEFAULT 'pending'
            )
        """)

        # Tags table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                category TEXT,
                usage_count INTEGER DEFAULT 0
            )
        """)

        # Document-Tags relationship
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_tags (
                document_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                confidence REAL DEFAULT 1.0,
                source TEXT DEFAULT 'ai',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (document_id, tag_id),
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        """)

        # Document relationships
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_doc_id INTEGER NOT NULL,
                target_doc_id INTEGER NOT NULL,
                relationship_type TEXT NOT NULL,
                similarity_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_doc_id) REFERENCES documents(id) ON DELETE CASCADE,
                FOREIGN KEY (target_doc_id) REFERENCES documents(id) ON DELETE CASCADE,
                UNIQUE(source_doc_id, target_doc_id, relationship_type)
            )
        """)

        # Processing log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processing_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                operation TEXT NOT NULL,
                status TEXT NOT NULL,
                error_message TEXT,
                processing_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_path ON documents(path)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(processing_status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_document_tags_doc ON document_tags(document_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_document_tags_tag ON document_tags(tag_id)")

        conn.commit()
        conn.close()

    def add_document(self, path: str, title: str = None, summary: str = None,
                    content: str = None) -> int:
        """Add or update a document.

        Args:
            path: Document file path
            title: Document title
            summary: Document summary
            content: Document content (for hash calculation)

        Returns:
            Document ID
        """
        content_hash = None
        file_size = None
        word_count = None

        if content:
            content_hash = hashlib.md5(content.encode()).hexdigest()
            file_size = len(content.encode())
            word_count = len(content.split())

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO documents (path, title, summary, content_hash, file_size, word_count, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(path) DO UPDATE SET
                title = excluded.title,
                summary = excluded.summary,
                content_hash = excluded.content_hash,
                file_size = excluded.file_size,
                word_count = excluded.word_count,
                updated_at = CURRENT_TIMESTAMP
        """, (path, title, summary, content_hash, file_size, word_count))

        document_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return document_id

    def get_document(self, document_id: int = None, path: str = None) -> Optional[Dict]:
        """Get document by ID or path.

        Args:
            document_id: Document ID
            path: Document path

        Returns:
            Document dictionary or None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if document_id:
            cursor.execute("SELECT * FROM documents WHERE id = ?", (document_id,))
        elif path:
            cursor.execute("SELECT * FROM documents WHERE path = ?", (path,))
        else:
            conn.close()
            return None

        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    def update_document_status(self, document_id: int, status: str):
        """Update document processing status.

        Args:
            document_id: Document ID
            status: New status
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE documents
            SET processing_status = ?, last_processed = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, document_id))

        conn.commit()
        conn.close()

    def add_tag(self, name: str, category: str = None) -> int:
        """Add or get a tag.

        Args:
            name: Tag name
            category: Tag category

        Returns:
            Tag ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO tags (name, category)
            VALUES (?, ?)
            ON CONFLICT(name) DO UPDATE SET category = COALESCE(excluded.category, category)
        """, (name, category))

        tag_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return tag_id

    def tag_document(self, document_id: int, tag_name: str, confidence: float = 1.0,
                    source: str = 'ai'):
        """Add a tag to a document.

        Args:
            document_id: Document ID
            tag_name: Tag name
            confidence: Confidence score (0-1)
            source: Tag source ('ai' or 'manual')
        """
        tag_id = self.add_tag(tag_name)

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO document_tags (document_id, tag_id, confidence, source)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(document_id, tag_id) DO UPDATE SET
                confidence = excluded.confidence,
                source = excluded.source
        """, (document_id, tag_id, confidence, source))

        # Update tag usage count
        cursor.execute("""
            UPDATE tags SET usage_count = (
                SELECT COUNT(DISTINCT document_id) FROM document_tags WHERE tag_id = ?
            ) WHERE id = ?
        """, (tag_id, tag_id))

        conn.commit()
        conn.close()

    def get_document_tags(self, document_id: int) -> List[Dict]:
        """Get all tags for a document.

        Args:
            document_id: Document ID

        Returns:
            List of tag dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT t.*, dt.confidence, dt.source
            FROM tags t
            JOIN document_tags dt ON t.id = dt.tag_id
            WHERE dt.document_id = ?
            ORDER BY dt.confidence DESC
        """, (document_id,))

        tags = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return tags

    def add_relationship(self, source_doc_id: int, target_doc_id: int,
                        relationship_type: str, similarity_score: float = None):
        """Add a relationship between documents.

        Args:
            source_doc_id: Source document ID
            target_doc_id: Target document ID
            relationship_type: Type of relationship
            similarity_score: Similarity score (0-1)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO document_relationships
                (source_doc_id, target_doc_id, relationship_type, similarity_score)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(source_doc_id, target_doc_id, relationship_type) DO UPDATE SET
                similarity_score = excluded.similarity_score
        """, (source_doc_id, target_doc_id, relationship_type, similarity_score))

        conn.commit()
        conn.close()

    def log_processing(self, document_id: int, operation: str, status: str,
                      error_message: str = None, processing_time: float = None):
        """Log a processing operation.

        Args:
            document_id: Document ID
            operation: Operation name
            status: Status ('success', 'failed', 'skipped')
            error_message: Error message if failed
            processing_time: Time taken in seconds
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO processing_log
                (document_id, operation, status, error_message, processing_time)
            VALUES (?, ?, ?, ?, ?)
        """, (document_id, operation, status, error_message, processing_time))

        conn.commit()
        conn.close()

    def search_documents_by_tag(self, tag_name: str) -> List[Dict]:
        """Search documents by tag name.

        Args:
            tag_name: Tag name to search

        Returns:
            List of document dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT d.*, GROUP_CONCAT(t.name) as tags
            FROM documents d
            JOIN document_tags dt ON d.id = dt.document_id
            JOIN tags t ON dt.tag_id = t.id
            WHERE t.name = ?
            GROUP BY d.id
        """, (tag_name,))

        documents = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return documents

    def needs_processing(self, path: str, content: str) -> bool:
        """Check if document needs processing based on content hash.

        Args:
            path: Document path
            content: Document content

        Returns:
            True if document needs processing
        """
        doc = self.get_document(path=path)
        if not doc:
            return True

        content_hash = hashlib.md5(content.encode()).hexdigest()
        return doc.get('content_hash') != content_hash

    def get_all_documents(self, status: str = None) -> List[Dict]:
        """Get all documents, optionally filtered by status.

        Args:
            status: Filter by processing status

        Returns:
            List of document dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if status:
            cursor.execute(
                "SELECT * FROM documents WHERE processing_status = ? ORDER BY updated_at DESC",
                (status,)
            )
        else:
            cursor.execute("SELECT * FROM documents ORDER BY updated_at DESC")

        documents = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return documents


# Global database instance
_db = None


def get_db(db_path: str = None) -> Database:
    """Get global database instance.

    Args:
        db_path: Path to database file (only used on first call)

    Returns:
        Database instance
    """
    global _db
    if _db is None:
        _db = Database(db_path)
    return _db
