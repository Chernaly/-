"""Base exporter interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional

from src.core.database import get_db
from src.core.config import get_config


class BaseExporter(ABC):
    """Base class for document exporters."""

    def __init__(self):
        """Initialize exporter."""
        self.db = get_db()
        self.config = get_config()

    @property
    @abstractmethod
    def format_name(self) -> str:
        """Return format name."""
        pass

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """Return file extension."""
        pass

    def export_all(self, output_dir: str) -> Dict:
        """Export all documents.

        Args:
            output_dir: Output directory path

        Returns:
            Export result dictionary
        """
        documents = self.db.get_all_documents()
        return self.export_documents([doc['id'] for doc in documents], output_dir)

    @abstractmethod
    def export_documents(self, document_ids: List[int], output_dir: str) -> Dict:
        """Export specific documents.

        Args:
            document_ids: List of document IDs
            output_dir: Output directory path

        Returns:
            Export result dictionary with 'count' and 'path'
        """
        pass

    def _ensure_output_dir(self, output_dir: str) -> Path:
        """Ensure output directory exists.

        Args:
            output_dir: Output directory path

        Returns:
            Path object
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path
