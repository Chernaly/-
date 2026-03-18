"""Main entry point for the knowledge management system."""

import argparse
import logging
import sys
from pathlib import Path

from src.core.config import get_config
from src.core.database import get_db
from src.monitors.file_watcher import create_watcher
from src.processors import create_processor
from src.qa.answer_generator import get_answer_generator
from src.search.search_engine import get_search_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('knowledge_system.log')
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Knowledge Management System')
    parser.add_argument('command', choices=['watch', 'process', 'search', 'ask', 'status'],
                       help='Command to run')
    parser.add_argument('--dir', default='./docs/watched',
                       help='Directory to watch/process')
    parser.add_argument('--query', '-q', help='Search query or question')
    parser.add_argument('--method', '-m', default='hybrid',
                       choices=['keyword', 'semantic', 'hybrid'],
                       help='Search method')
    parser.add_argument('--tags', '-t', nargs='+', help='Filter by tags')
    parser.add_argument('--limit', '-l', type=int, default=10,
                       help='Maximum results')

    args = parser.parse_args()

    # Initialize configuration
    try:
        config = get_config()
        config.validate()
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    # Execute command
    if args.command == 'watch':
        cmd_watch(args, config)
    elif args.command == 'process':
        cmd_process(args, config)
    elif args.command == 'search':
        cmd_search(args, config)
    elif args.command == 'ask':
        cmd_ask(args, config)
    elif args.command == 'status':
        cmd_status(args, config)


def cmd_watch(args, config):
    """Start file watcher."""
    logger.info("Starting file watcher...")

    processor = create_processor(config)
    watcher = create_watcher(config.watcher, processor.process_document)

    # Scan existing files first
    watcher.scan_existing_files()

    # Start watching
    watcher.run()


def cmd_process(args, config):
    """Process documents in directory."""
    logger.info(f"Processing documents in {args.dir}...")

    processor = create_processor(config)
    results = processor.batch_process(args.dir)

    # Print summary
    success = sum(1 for r in results if r['status'] == 'success')
    failed = sum(1 for r in results if r['status'] == 'failed')
    skipped = sum(1 for r in results if r['status'] == 'skipped')

    print(f"\nProcessing complete:")
    print(f"  Success: {success}")
    print(f"  Failed: {failed}")
    print(f"  Skipped: {skipped}")
    print(f"  Total: {len(results)}")

    if failed > 0:
        print("\nFailed documents:")
        for r in results:
            if r['status'] == 'failed':
                print(f"  - {r['file_path']}: {r.get('error', 'Unknown error')}")


def cmd_search(args, config):
    """Search documents."""
    if not args.query:
        logger.error("Search query required. Use --query or -q")
        sys.exit(1)

    logger.info(f"Searching for: {args.query}")

    search_engine = get_search_engine()
    results = search_engine.search(
        query=args.query,
        method=args.method,
        max_results=args.limit,
        tags=args.tags
    )

    print(f"\nFound {len(results)} results:\n")

    for i, result in enumerate(results, 1):
        print(f"{i}. {result.get('title', 'Untitled')}")
        print(f"   Path: {result.get('path', 'N/A')}")
        if result.get('summary'):
            print(f"   Summary: {result['summary'][:100]}...")
        if result.get('tags'):
            print(f"   Tags: {result['tags']}")
        print(f"   Score: {result.get('score', 0):.3f} ({result.get('search_method', 'unknown')})")
        print()


def cmd_ask(args, config):
    """Ask a question."""
    if not args.query:
        logger.error("Question required. Use --query or -q")
        sys.exit(1)

    logger.info(f"Question: {args.query}")

    answer_generator = get_answer_generator()
    result = answer_generator.answer_question(args.query, max_context=args.limit)

    print(f"\nQuestion: {result['question']}\n")
    print(f"Answer:\n{result['answer']}\n")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Based on {result['context_count']} document(s)")

    if result['context']:
        print("\nSources:")
        for i, ctx in enumerate(result['context'][:3], 1):
            print(f"  {i}. {ctx['title']}")


def cmd_status(args, config):
    """Show system status."""
    db = get_db()
    search_engine = get_search_engine()

    # Get statistics
    documents = db.get_all_documents()
    pending = sum(1 for d in documents if d['processing_status'] == 'pending')
    completed = sum(1 for d in documents if d['processing_status'] == 'completed')
    failed = sum(1 for d in documents if d['processing_status'] == 'failed')

    print("\n=== Knowledge Management System Status ===\n")
    print(f"Documents: {len(documents)}")
    print(f"  Completed: {completed}")
    print(f"  Pending: {pending}")
    print(f"  Failed: {failed}")
    print(f"\nVector Store: {search_engine.vector_store.get_document_count() if search_engine.vector_store else 'Not available'} documents")
    print(f"\nWatch Directory: {args.dir}")
    print(f"Database: {config.database.get('sqlite', 'N/A')}")
    print(f"Vector Store: {config.database.get('chroma', 'N/A')}")
    print(f"Claude API: {'Configured' if config.claude.get('api_key') != 'your_api_key_here' else 'Not configured'}")
    print()


if __name__ == '__main__':
    main()
