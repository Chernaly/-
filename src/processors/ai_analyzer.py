"""AI analyzer using Claude API."""

import logging
import time
from typing import Dict, List, Optional

import anthropic

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """Analyzes documents using Claude API."""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022",
                 max_tokens: int = 1024, temperature: float = 0.3):
        """Initialize AI analyzer.

        Args:
            api_key: Claude API key
            model: Model name
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def analyze_document(self, content: str, title: str = None,
                        existing_tags: List[str] = None) -> Dict:
        """Analyze a document and generate metadata.

        Args:
            content: Document content
            title: Document title
            existing_tags: Existing tags to consider

        Returns:
            Dictionary with 'summary' and 'tags'
        """
        prompt = self._build_analysis_prompt(content, title, existing_tags)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            analysis_text = response.content[0].text
            return self._parse_analysis_response(analysis_text)

        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            raise

    def _build_analysis_prompt(self, content: str, title: str = None,
                               existing_tags: List[str] = None) -> str:
        """Build analysis prompt.

        Args:
            content: Document content
            title: Document title
            existing_tags: Existing tags

        Returns:
            Analysis prompt
        """
        # Truncate content if too long
        max_content_length = 4000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."

        prompt = f"""Analyze the following document and provide:
1. A concise summary (100-200 words)
2. 3-7 relevant tags

Document title: {title or 'Untitled'}

Document content:
{content}
"""

        if existing_tags:
            prompt += f"\nExisting tags: {', '.join(existing_tags)}\n"
            prompt += "Consider these existing tags when generating new tags.\n"

        prompt += """
Format your response exactly as:
SUMMARY:
[Your summary here]

TAGS:
[tag1, tag2, tag3, ...]
"""

        return prompt

    def _parse_analysis_response(self, response: str) -> Dict:
        """Parse analysis response from Claude.

        Args:
            response: Response text

        Returns:
            Dictionary with 'summary' and 'tags'
        """
        result = {
            'summary': '',
            'tags': []
        }

        # Extract summary
        summary_match = response.split('SUMMARY:')
        if len(summary_match) > 1:
            summary_text = summary_match[1].split('TAGS:')[0]
            result['summary'] = summary_text.strip()

        # Extract tags
        tags_match = response.split('TAGS:')
        if len(tags_match) > 1:
            tags_text = tags_match[1].strip()
            # Remove brackets and parse tags
            tags_text = tags_text.replace('[', '').replace(']', '')
            tags = [tag.strip().strip('"\'') for tag in tags_text.split(',')]
            result['tags'] = [tag for tag in tags if tag]

        return result

    def generate_answer(self, question: str, context: List[Dict],
                       max_context_length: int = 3000) -> str:
        """Generate answer based on question and context.

        Args:
            question: User question
            context: List of context documents with 'title' and 'content'
            max_context_length: Maximum context length

        Returns:
            Generated answer
        """
        # Build context string
        context_parts = []
        current_length = 0

        for doc in context:
            doc_text = f"\n---\nDocument: {doc['title']}\n{doc['content']}\n---\n"

            if current_length + len(doc_text) > max_context_length:
                break

            context_parts.append(doc_text)
            current_length += len(doc_text)

        context_str = ''.join(context_parts)

        prompt = f"""Based on the following documents, answer the question.
Include citations by mentioning which document(s) the information comes from.

Context documents:
{context_str}

Question: {question}

Provide a clear, concise answer with citations:"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response.content[0].text

        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            raise

    def extract_keywords(self, content: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from content.

        Args:
            content: Document content
            max_keywords: Maximum number of keywords

        Returns:
            List of keywords
        """
        prompt = f"""Extract {max_keywords} most important keywords from the following text.
Return only the keywords, one per line.

Text:
{content[:2000]}
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            keywords_text = response.content[0].text
            keywords = [kw.strip() for kw in keywords_text.split('\n') if kw.strip()]
            return keywords[:max_keywords]

        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            return []

    def batch_analyze(self, documents: List[Dict],
                     batch_delay: float = 1.0) -> List[Dict]:
        """Analyze multiple documents with rate limiting.

        Args:
            documents: List of documents with 'content' and 'title'
            batch_delay: Delay between API calls in seconds

        Returns:
            List of analysis results
        """
        results = []

        for i, doc in enumerate(documents):
            logger.info(f"Analyzing document {i+1}/{len(documents)}: {doc.get('title')}")

            try:
                result = self.analyze_document(
                    content=doc['content'],
                    title=doc.get('title'),
                    existing_tags=doc.get('existing_tags')
                )
                results.append(result)

                # Rate limiting
                if i < len(documents) - 1:
                    time.sleep(batch_delay)

            except Exception as e:
                logger.error(f"Error analyzing document {doc.get('title')}: {e}")
                results.append({
                    'summary': '',
                    'tags': [],
                    'error': str(e)
                })

        return results
