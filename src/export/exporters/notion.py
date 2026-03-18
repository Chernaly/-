"""Notion format exporter."""

import csv
from pathlib import Path
from typing import Dict, List
from datetime import datetime

from .base import BaseExporter


class NotionExporter(BaseExporter):
    """Export to Notion-compatible format (CSV for database import)."""

    @property
    def format_name(self) -> str:
        return "Notion"

    @property
    def file_extension(self) -> str:
        return ".md"

    def export_documents(self, document_ids: List[int], output_dir: str) -> Dict:
        """Export documents to Notion format.

        Args:
            document_ids: List of document IDs to export
            output_dir: Output directory path

        Returns:
            Dictionary with 'count' and 'path' keys
        """
        output_path = self._ensure_output_dir(output_dir)
        exported_count = 0

        # Create CSV file for Notion database import
        csv_file = output_path / "notion_import.csv"

        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(['Title', 'Tags', 'Summary', 'Content', 'Date', 'Status'])

            for doc_id in document_ids:
                doc = self.db.get_document(document_id=doc_id)
                if not doc:
                    continue

                # Read original content
                try:
                    with open(doc['path'], 'r', encoding='utf-8') as file:
                        content = file.read()
                except FileNotFoundError:
                    continue

                # Get tags
                tags = self.db.get_document_tags(doc['id'])
                tag_names = ', '.join([tag['name'] for tag in tags])

                # Write row
                writer.writerow([
                    doc.get('title', 'Untitled'),
                    tag_names,
                    doc.get('summary', ''),
                    content,
                    doc.get('created_at', ''),
                    doc.get('processing_status', '')
                ])

                exported_count += 1

        # Also export individual markdown files
        for doc_id in document_ids:
            doc = self.db.get_document(document_id=doc_id)
            if not doc:
                continue

            try:
                with open(doc['path'], 'r', encoding='utf-8') as f:
                    content = f.read()
            except FileNotFoundError:
                continue

            # Create Notion-compatible markdown
            tags = self.db.get_document_tags(doc['id'])
            tag_names = [tag['name'] for tag in tags]

            notion_content = self._format_for_notion(doc, content, tag_names)

            output_file = output_path / f"{Path(doc['path']).stem}{self.file_extension}"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(notion_content)

        return {
            'count': exported_count,
            'path': str(csv_file)
        }

    def _format_for_notion(self, doc: Dict, content: str, tags: List[str]) -> str:
        """Format document for Notion.

        Args:
            doc: Document dictionary
            content: Document content
            tags: List of tags

        Returns:
            Formatted content
        """
        # Add properties as comments (Notion will recognize them)
        header = f"""<!--
Title: {doc.get('title', 'Untitled')}
Tags: {', '.join(tags)}
Date: {doc.get('created_at', '')}
Status: {doc.get('processing_status', '')}
-->

"""
        return header + content
