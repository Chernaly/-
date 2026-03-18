"""Markdown document parser and frontmatter manager."""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml
from ruamel.yaml import YAML


class MarkdownParser:
    """Parses markdown files and extracts metadata."""

    def __init__(self):
        """Initialize parser."""
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.default_flow_style = False

    def parse_file(self, file_path: str) -> Dict:
        """Parse a markdown file.

        Args:
            file_path: Path to markdown file

        Returns:
            Dictionary with 'frontmatter', 'content', 'sections'
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()

        return self.parse_text(text)

    def parse_text(self, text: str) -> Dict:
        """Parse markdown text.

        Args:
            text: Markdown text

        Returns:
            Dictionary with 'frontmatter', 'content', 'sections'
        """
        frontmatter, content = self._extract_frontmatter(text)

        return {
            'frontmatter': frontmatter or {},
            'content': content,
            'sections': self._extract_sections(content),
            'code_blocks': self._extract_code_blocks(content),
            'links': self._extract_links(content)
        }

    def _extract_frontmatter(self, text: str) -> Tuple[Optional[Dict], str]:
        """Extract YAML frontmatter from markdown.

        Args:
            text: Markdown text

        Returns:
            Tuple of (frontmatter_dict, remaining_content)
        """
        pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(pattern, text, re.DOTALL)

        if match:
            try:
                frontmatter = yaml.safe_load(match.group(1))
                content = text[match.end():]
                return frontmatter, content
            except yaml.YAMLError:
                pass

        return None, text

    def _extract_sections(self, content: str) -> List[Dict]:
        """Extract sections from markdown content.

        Args:
            content: Markdown content

        Returns:
            List of section dictionaries
        """
        sections = []
        pattern = r'^(#{1,6})\s+(.+)$'

        for match in re.finditer(pattern, content, re.MULTILINE):
            level = len(match.group(1))
            title = match.group(2).strip()
            start = match.start()

            # Find section content (until next heading)
            next_match = re.search(pattern, content[start + match.end():], re.MULTILINE)
            if next_match:
                end = start + match.end() + next_match.start()
            else:
                end = len(content)

            section_content = content[start:end].strip()

            sections.append({
                'level': level,
                'title': title,
                'content': section_content,
                'start': start,
                'end': end
            })

        return sections

    def _extract_code_blocks(self, content: str) -> List[Dict]:
        """Extract code blocks from markdown.

        Args:
            content: Markdown content

        Returns:
            List of code block dictionaries
        """
        code_blocks = []
        pattern = r'```(\w+)?\s*\n(.*?)\n```'

        for match in re.finditer(pattern, content, re.DOTALL):
            code_blocks.append({
                'language': match.group(1) or 'text',
                'code': match.group(2),
                'start': match.start(),
                'end': match.end()
            })

        return code_blocks

    def _extract_links(self, content: str) -> List[Dict]:
        """Extract links from markdown.

        Args:
            content: Markdown content

        Returns:
            List of link dictionaries
        """
        links = []

        # Markdown links: [text](url)
        md_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        for match in re.finditer(md_pattern, content):
            links.append({
                'type': 'markdown',
                'text': match.group(1),
                'url': match.group(2)
            })

        # Wiki-style links: [[page]]
        wiki_pattern = r'\[\[([^\]]+)\]\]'
        for match in re.finditer(wiki_pattern, content):
            links.append({
                'type': 'wiki',
                'text': match.group(1),
                'url': match.group(1)
            })

        return links

    def update_frontmatter(self, file_path: str, metadata: Dict,
                          preserve_existing: bool = True) -> bool:
        """Update frontmatter in a markdown file.

        Args:
            file_path: Path to markdown file
            metadata: Metadata to add/update
            preserve_existing: Whether to preserve existing metadata

        Returns:
            True if successful
        """
        path = Path(file_path)

        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()

        existing_frontmatter, content = self._extract_frontmatter(text)

        if existing_frontmatter is None:
            existing_frontmatter = {}

        # Merge metadata
        if preserve_existing:
            # Don't overwrite existing manual tags
            if 'tags' in metadata and 'tags' in existing_frontmatter:
                existing_tags = set(existing_frontmatter['tags'])
                new_tags = set(metadata['tags'])
                metadata['tags'] = list(existing_tags | new_tags)

            final_metadata = {**metadata, **existing_frontmatter}
        else:
            final_metadata = metadata

        # Create new frontmatter
        from io import StringIO
        stream = StringIO()
        self.yaml.dump(final_metadata, stream)
        frontmatter_text = f"---\n{stream.getvalue()}---\n"

        # Write updated file
        with open(path, 'w', encoding='utf-8') as f:
            f.write(frontmatter_text + content)

        return True

    def get_title(self, parsed: Dict) -> str:
        """Extract title from parsed document.

        Args:
            parsed: Parsed document dictionary

        Returns:
            Document title
        """
        # Check frontmatter first
        if parsed['frontmatter'] and 'title' in parsed['frontmatter']:
            return parsed['frontmatter']['title']

        # Check first heading
        if parsed['sections']:
            return parsed['sections'][0]['title']

        # Use filename
        return "Untitled"

    def get_text_content(self, content: str) -> str:
        """Get plain text from markdown content.

        Args:
            content: Markdown content

        Returns:
            Plain text
        """
        # Remove code blocks
        text = re.sub(r'```.*?\n.*?\n```', '', content, flags=re.DOTALL)

        # Remove inline code
        text = re.sub(r'`[^`]+`', '', text)

        # Remove links but keep text
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)

        # Remove headings markers
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)

        # Remove emphasis
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)

        # Remove extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()

        return text
