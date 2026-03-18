#!/usr/bin/env python
"""Main entry point with all features."""

import argparse
import sys

# Web interface
def start_web(host="0.0.0.0", port=8000):
    """Start web interface."""
    from web.app import start_web_server
    start_web_server(host, port)

# Enhanced CLI
def start_cli():
    """Start enhanced CLI."""
    from cli_enhanced import main as cli_main
    cli_main()

# Original CLI
def start_original_cli():
    """Start original CLI."""
    import main as original_main
    original_main.main()

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='智能知识管理系统 - Intelligent Knowledge Management System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start web interface
  python start.py web --port 8080

  # Start interactive CLI with rich interface
  python start.py cli

  # Use original CLI
  python start.py original --help

  # Process documents
  python start.py original process --dir ./docs/watched
        """
    )

    subparsers = parser.add_subparsers(dest='interface', help='Interface to use')

    # Web interface
    web_parser = subparsers.add_parser('web', help='Start web interface')
    web_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    web_parser.add_argument('--port', type=int, default=8000, help='Port to bind to')

    # Enhanced CLI
    cli_parser = subparsers.add_parser('cli', help='Start enhanced CLI with Rich interface')
    cli_parser.add_argument('command', nargs='?', choices=['menu', 'search', 'qa', 'status', 'list'],
                           default='menu', help='CLI command')

    # Original CLI
    original_parser = subparsers.add_parser('original', help='Use original CLI')
    original_parser.add_argument('args', nargs=argparse.REMAINDER, help='Arguments for original CLI')

    args = parser.parse_args()

    if args.interface == 'web':
        print(f"\n🌐 Starting web interface at http://{args.host}:{args.port}")
        print("📚 API documentation will be available at /docs")
        print("Press Ctrl+C to stop\n")
        start_web(args.host, args.port)

    elif args.interface == 'cli':
        sys.argv = ['cli_enhanced.py'] + ([args.command] if args.command != 'menu' else [])
        start_cli()

    elif args.interface == 'original':
        if args.args:
            sys.argv = ['main.py'] + args.args
        start_original_cli()

    else:
        # Default: show help
        parser.print_help()
        print("\n💡 Quick Start:")
        print("   python start.py web        # Start web interface")
        print("   python start.py cli        # Start enhanced CLI")
        print("   python start.py original   # Use original CLI")

if __name__ == '__main__':
    main()
