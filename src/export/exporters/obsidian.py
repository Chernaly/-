"""Obsidian format exporter."""

import yaml
from pathlib import Path
from typing import Dict, List

from .base import BaseExporter


class ObsidianExporter(BaseExporter):
    """Export to Obsidian-compatible markdown format."""

    @property
    def format_name(self) -> str:
        return "Obsidian"

    @property
    def file_extension(self) -> str:
        return ".md"

    def export_documents(self, document_ids: List[int], output_dir: str) -> Dict:
        """Export documents to Obsidian format.

        Args:
            document_ids: List of document IDs to export
            output_dir: Output directory path

        Returns:
            Dictionary with 'count' and 'path' keys
        """
        output_path = self._ensure_output_dir(output_dir)
        exported_count = 0

        for doc_id in document_ids:
            doc = self.db.get_document(document_id=doc_id)
            if not doc:
                continue

            # Read original document
            try:
                with open(doc['path'], 'r', encoding='utf-8') as f:
                    content = f.read()
            except FileNotFoundError:
                continue

            # Create Obsidian frontmatter
            frontmatter = self._create_obsidian_frontmatter(doc)

            # Create new document with frontmatter
            new_content = f"---\n{yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False)}---\n\n{content}"

            # Write to output file
            output_file = output_path / f"{Path(doc['path']).stem}{self.file_extension}"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(new_content)

            exported_count += 1

        return {
            'count': exported_count,
            'path': str(output_path)
        }

    def _create_obsidian_frontmatter(self, doc: Dict) -> Dict:
        """Create Obsidian-compatible frontmatter.

        Args:
            doc: Document dictionary

        Returns:
            Frontmatter dictionary
        """
        # Get tags
        tags = self.db.get_document_tags(doc['id'])
        tag_names = [tag['name'] for tag in tags]

        frontmatter = {
            'title': doc.get('title', 'Untitled'),
            'date': doc.get('created_at', ''),
            'tags': tag_names,
            'aliases': [],
            'type': 'note'
        }

        if doc.get('summary'):
            frontmatter['summary'] = doc['summary']

        return frontmatter
