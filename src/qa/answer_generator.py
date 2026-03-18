"""Answer generator using Claude API."""

import logging
from typing import Dict, List

from ..core.config import get_config
from ..processors.ai_analyzer import AIAnalyzer
from .query_engine import get_query_engine

logger = logging.getLogger(__name__)


class AnswerGenerator:
    """Generates answers to questions based on knowledge base."""

    def __init__(self):
        """Initialize answer generator."""
        self.config = get_config()
        self.query_engine = get_query_engine()
        self.analyzer = None

        # Initialize AI analyzer if available
        api_key = self.config.claude.get('api_key')
        if api_key and api_key != 'your_api_key_here':
            self.analyzer = AIAnalyzer(
                api_key=api_key,
                model=self.config.claude.get('model', 'claude-3-5-sonnet-20241022'),
                max_tokens=self.config.claude.get('max_tokens', 1024),
                temperature=self.config.claude.get('temperature', 0.3)
            )

    def answer_question(self, question: str, max_context: int = 5) -> Dict:
        """Answer a question based on the knowledge base.

        Args:
            question: User question
            max_context: Maximum context documents

        Returns:
            Answer dictionary
        """
        # Process query to get context
        query_result = self.query_engine.process_query(question, max_context)

        result = {
            'question': question,
            'answer': None,
            'context': query_result['context'],
            'context_count': query_result['context_count'],
            'keywords': query_result['keywords'],
            'confidence': 0.0
        }

        if not query_result['context']:
            result['answer'] = "I couldn't find any relevant information in the knowledge base."
            result['confidence'] = 0.0
            return result

        # Generate answer using AI
        if self.analyzer:
            try:
                answer = self.analyzer.generate_answer(
                    question=question,
                    context=query_result['context'],
                    max_context_length=3000
                )
                result['answer'] = answer

                # Estimate confidence based on context scores
                avg_score = sum(c['score'] for c in query_result['context']) / len(query_result['context'])
                result['confidence'] = min(avg_score, 1.0)

            except Exception as e:
                logger.error(f"Error generating answer: {e}")
                result['answer'] = f"Error generating answer: {str(e)}"
                result['confidence'] = 0.0
        else:
            # Fallback: return context summaries
            result['answer'] = self._generate_fallback_answer(query_result['context'])
            result['confidence'] = 0.5

        return result

    def _generate_fallback_answer(self, context: List[Dict]) -> str:
        """Generate a fallback answer without AI.

        Args:
            context: Context documents

        Returns:
            Fallback answer
        """
        if not context:
            return "No relevant information found."

        answer_parts = ["Based on the knowledge base:\n"]

        for i, doc in enumerate(context[:3], 1):
            answer_parts.append(f"\n{i}. From '{doc['title']}':")
            if doc.get('summary'):
                answer_parts.append(f"   {doc['summary']}")
            else:
                answer_parts.append(f"   (See document for details)")

        answer_parts.append("\n\nNote: This is a basic answer. Configure Claude API for intelligent answers.")

        return ''.join(answer_parts)

    def follow_up_questions(self, question: str, answer: str,
                           context: List[Dict]) -> List[str]:
        """Generate follow-up questions.

        Args:
            question: Original question
            answer: Generated answer
            context: Context documents

        Returns:
            List of follow-up questions
        """
        # Simple heuristic-based follow-up questions
        follow_ups = []

        if context:
            # Suggest exploring related documents
            for doc in context[:2]:
                if doc.get('tags'):
                    tag = doc['tags'][0] if isinstance(doc['tags'], list) else doc['tags'].split(',')[0]
                    follow_ups.append(f"Tell me more about {tag}")

        # Add generic follow-ups
        follow_ups.extend([
            "Can you provide more details?",
            "What are the related topics?",
            "Are there any examples?"
        ])

        return follow_ups[:5]


# Global answer generator instance
_answer_generator = None


def get_answer_generator() -> AnswerGenerator:
    """Get global answer generator instance.

    Returns:
        AnswerGenerator instance
    """
    global _answer_generator
    if _answer_generator is None:
        _answer_generator = AnswerGenerator()
    return _answer_generator
