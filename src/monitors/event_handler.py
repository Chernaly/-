"""File event handler for processing document changes."""

import logging
import time
from pathlib import Path
from typing import Callable, Optional

from watchdog.events import FileSystemEvent, FileSystemEventHandler

logger = logging.getLogger(__name__)


class MarkdownEventHandler(FileSystemEventHandler):
    """Handles file system events for markdown files."""

    def __init__(self, processor: Callable, extensions: list = None):
        """Initialize event handler.

        Args:
            processor: Callback function to process files
            extensions: List of file extensions to watch
        """
        super().__init__()
        self.processor = processor
        self.extensions = extensions or ['.md', '.markdown']
        self._last_processed = {}  # Track last processed times to avoid duplicates

    def _should_process(self, event: FileSystemEvent) -> bool:
        """Check if event should be processed.

        Args:
            event: File system event

        Returns:
            True if event should be processed
        """
        # Skip directories
        if event.is_directory:
            return False

        # Check file extension
        path = Path(event.src_path)
        if path.suffix.lower() not in self.extensions:
            return False

        # Skip temporary files
        if path.name.startswith('~') or path.name.startswith('.'):
            return False

        # Debounce: skip if processed recently (within 1 second)
        current_time = time.time()
        last_time = self._last_processed.get(event.src_path, 0)
        if current_time - last_time < 1.0:
            return False

        self._last_processed[event.src_path] = current_time
        return True

    def on_created(self, event: FileSystemEvent):
        """Handle file creation event.

        Args:
            event: File system event
        """
        if not self._should_process(event):
            return

        logger.info(f"File created: {event.src_path}")
        try:
            self.processor(event.src_path, event_type='created')
        except Exception as e:
            logger.error(f"Error processing created file {event.src_path}: {e}")

    def on_modified(self, event: FileSystemEvent):
        """Handle file modification event.

        Args:
            event: File system event
        """
        if not self._should_process(event):
            return

        logger.info(f"File modified: {event.src_path}")
        try:
            self.processor(event.src_path, event_type='modified')
        except Exception as e:
            logger.error(f"Error processing modified file {event.src_path}: {e}")

    def on_deleted(self, event: FileSystemEvent):
        """Handle file deletion event.

        Args:
            event: File system event
        """
        if not self._should_process(event):
            return

        logger.info(f"File deleted: {event.src_path}")
        # Could implement cleanup logic here if needed

    def on_moved(self, event: FileSystemEvent):
        """Handle file move event.

        Args:
            event: File system event
        """
        if not self._should_process(event):
            return

        logger.info(f"File moved: {event.src_path} -> {event.dest_path}")
        # Could handle file renames here if needed
