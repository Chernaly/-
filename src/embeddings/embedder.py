"""Text chunking utilities for embedding generation."""


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> list:
    """Split text into overlapping chunks.

    Args:
        text: Text to chunk
        chunk_size: Target size of each chunk in characters
        overlap: Overlap between chunks in characters

    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Try to find a good break point
        if end < len(text):
            # Look for paragraph break
            break_point = text.rfind('\n\n', start, end)
            if break_point > start:
                end = break_point
            else:
                # Look for sentence break
                break_point = text.rfind('. ', start, end)
                if break_point > start:
                    end = break_point + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap if end < len(text) else end

    return chunks


def chunk_by_sections(sections: list, max_chunk_size: int = 1500) -> list:
    """Chunk document by sections.

    Args:
        sections: List of section dictionaries
        max_chunk_size: Maximum chunk size

    Returns:
        List of chunk dictionaries
    """
    chunks = []

    for section in sections:
        content = section.get('content', '')

        if len(content) <= max_chunk_size:
            chunks.append({
                'content': content,
                'title': section.get('title'),
                'level': section.get('level'),
                'type': 'section'
            })
        else:
            # Split large sections
            sub_chunks = chunk_text(content, chunk_size=max_chunk_size)
            for i, sub_chunk in enumerate(sub_chunks):
                chunks.append({
                    'content': sub_chunk,
                    'title': f"{section.get('title')} (part {i+1})",
                    'level': section.get('level'),
                    'type': 'section_chunk',
                    'part': i + 1
                })

    return chunks
