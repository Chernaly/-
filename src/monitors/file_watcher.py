"""File watcher for monitoring markdown files."""

import logging
import time
from pathlib import Path
from threading import Thread
from typing import Callable, List

from watchdog.observers import Observer

from .event_handler import MarkdownEventHandler

logger = logging.getLogger(__name__)


class FileWatcher:
    """Monitors directories for file changes."""

    def __init__(self, directories: List[str], processor: Callable,
                 extensions: List[str] = None):
        """Initialize file watcher.

        Args:
            directories: List of directories to watch
            processor: Callback function to process files
            extensions: List of file extensions to watch
        """
        self.directories = [Path(d) for d in directories]
        self.processor = processor
        self.extensions = extensions or ['.md', '.markdown']
        self.observer = Observer()
        self.event_handler = MarkdownEventHandler(processor, self.extensions)
        self._running = False

    def start(self):
        """Start watching directories."""
        if self._running:
            logger.warning("File watcher is already running")
            return

        for directory in self.directories:
            if not directory.exists():
                logger.warning(f"Directory does not exist: {directory}")
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {directory}")

            self.observer.schedule(self.event_handler, str(directory), recursive=True)
            logger.info(f"Watching directory: {directory}")

        self.observer.start()
        self._running = True
        logger.info("File watcher started")

    def stop(self):
        """Stop watching directories."""
        if not self._running:
            return

        self.observer.stop()
        self.observer.join()
        self._running = False
        logger.info("File watcher stopped")

    def run(self):
        """Run the watcher in blocking mode."""
        self.start()
        try:
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.stop()

    def run_in_thread(self) -> Thread:
        """Run the watcher in a background thread.

        Returns:
            Thread object
        """
        thread = Thread(target=self.run, daemon=True)
        thread.start()
        return thread

    def is_running(self) -> bool:
        """Check if watcher is running.

        Returns:
            True if watcher is running
        """
        return self._running

    def scan_existing_files(self):
        """Scan and process existing files in watched directories."""
        logger.info("Scanning existing files...")

        for directory in self.directories:
            if not directory.exists():
                continue

            for ext in self.extensions:
                for file_path in directory.rglob(f"*{ext}"):
                    if file_path.name.startswith('~') or file_path.name.startswith('.'):
                        continue

                    logger.info(f"Found existing file: {file_path}")
                    try:
                        self.processor(str(file_path), event_type='scan')
                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {e}")

        logger.info("Finished scanning existing files")


def create_watcher(config: dict, processor: Callable) -> FileWatcher:
    """Create a file watcher from configuration.

    Args:
        config: Configuration dictionary
        processor: Callback function to process files

    Returns:
        FileWatcher instance
    """
    return FileWatcher(
        directories=config.get('directories', ['./docs/watched']),
        processor=processor,
        extensions=config.get('extensions', ['.md', '.markdown'])
    )
