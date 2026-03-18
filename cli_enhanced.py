"""Enhanced CLI with Rich terminal interface."""

import logging
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich import print as rprint

from src.core.config import get_config
from src.core.database import get_db
from src.monitors.file_watcher import create_watcher
from src.processors import create_processor
from src.qa.answer_generator import get_answer_generator
from src.search.search_engine import get_search_engine

console = Console()
logger = logging.getLogger(__name__)


class EnhancedCLI:
    """Enhanced CLI interface with Rich."""

    def __init__(self):
        """Initialize CLI."""
        self.config = get_config()
        self.db = get_db()

    def show_banner(self):
        """Display application banner."""
        banner = """
[bold cyan]╔════════════════════════════════════════════════════════════╗[/bold cyan]
[bold cyan]║[/bold cyan]  [bold yellow]🧠 智能知识管理系统[/bold yellow]                              [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]  [dim]AI-Powered Knowledge Management System[/dim]              [bold cyan]║[/bold cyan]
[bold cyan]╚════════════════════════════════════════════════════════════╝[/bold cyan]
        """
        console.print(banner)

    def show_status(self):
        """Show system status."""
        documents = self.db.get_all_documents()

        stats = {
            "total": len(documents),
            "completed": sum(1 for d in documents if d["processing_status"] == "completed"),
            "pending": sum(1 for d in documents if d["processing_status"] == "pending"),
            "failed": sum(1 for d in documents if d["processing_status"] == "failed"),
        }

        # Create status table
        table = Table(title="📊 系统状态", show_header=False)
        table.add_column("指标", style="cyan")
        table.add_column("值", justify="right", style="green")

        table.add_row("📄 文档总数", str(stats["total"]))
        table.add_row("✅ 已处理", str(stats["completed"]))
        table.add_row("⏳ 待处理", str(stats["pending"]))
        table.add_row("❌ 处理失败", str(stats["failed"]))

        console.print(table)

        # Show configuration
        config_table = Table(title="⚙️  配置信息", show_header=False)
        config_table.add_column("配置项", style="cyan")
        config_table.add_column("值", style="yellow")

        config_table.add_row("监视目录", ", ".join(self.config.watcher.get('directories', [])))
        config_table.add_row("数据库", self.config.database.get('sqlite', 'N/A'))
        config_table.add_row("Claude API", "✅ 已配置" if self.config.claude.get('api_key') else "❌ 未配置")

        console.print(config_table)

    def interactive_search(self):
        """Interactive search mode."""
        console.clear()
        self.show_banner()
        console.print("\n[bold cyan]🔍 文档搜索[/bold cyan]\n")

        while True:
            query = Prompt.ask("\n[a]输入搜索关键词[/a] (输入 'quit' 退出)", default="")

            if query.lower() in ['quit', 'exit', 'q']:
                break

            if not query.strip():
                continue

            # Ask for search method
            method = Prompt.ask(
                "选择搜索方法",
                choices=["keyword", "semantic", "hybrid"],
                default="hybrid"
            )

            with console.status("[bold green]搜索中..."):
                search_engine = get_search_engine()
                results = search_engine.search(query=query, method=method, max_results=10)

            if not results:
                console.print("\n[yellow]没有找到相关文档[/yellow]")
                continue

            # Display results
            console.print(f"\n[bold green]找到 {len(results)} 个结果:[/bold green]\n")

            for i, result in enumerate(results, 1):
                title = result.get('title', '无标题')
                score = result.get('score', 0) * 100
                path = result.get('path', '')
                summary = result.get('summary', '')

                console.print(Panel(
                    f"[bold cyan]{i}. {title}[/bold cyan]\n"
                    f"[dim]{path}[/dim]\n\n"
                    f"{summary[:150]}{'...' if len(summary) > 150 else ''}\n\n"
                    f"[green]相关度: {score:.1f}%[/green]",
                    title=f"[bold]{title}[/bold]",
                    border_style="blue"
                ))

            if Confirm.ask("\n继续搜索?"):
                continue
            else:
                break

    def interactive_qa(self):
        """Interactive Q&A mode."""
        console.clear()
        self.show_banner()
        console.print("\n[bold cyan]💬 智能问答[/bold cyan]\n")
        console.print("[dim]输入你的问题，系统会基于知识库给出答案[/dim]\n")

        answer_generator = get_answer_generator()

        while True:
            question = Prompt.ask("\n[a]问题[/a] (输入 'quit' 退出)")

            if question.lower() in ['quit', 'exit', 'q']:
                break

            if not question.strip():
                continue

            with console.status("[bold green]思考中..."):
                result = answer_generator.answer_question(question)

            # Display answer
            console.print(f"\n[bold green]回答:[/bold green]")
            console.print(Panel(result['answer'], border_style="green"))

            # Display confidence
            confidence_color = "green" if result['confidence'] > 0.7 else "yellow"
            console.print(f"\n[{confidence_color}]置信度: {result['confidence']:.1%}[/{confidence_color}]")

            # Display sources
            if result['context']:
                console.print(f"\n[dim]基于 {result['context_count']} 个文档:[/dim]")
                for i, ctx in enumerate(result['context'][:3], 1):
                    console.print(f"  {i}. [cyan]{ctx['title']}[/cyan]")

            if not Confirm.ask("\n继续提问?"):
                break

    def process_documents(self, directory: str):
        """Process documents with progress bar."""
        console.clear()
        self.show_banner()
        console.print(f"\n[bold cyan]📄 处理文档[/bold cyan]\n")

        processor = create_processor(self.config)
        dir_path = Path(directory)

        if not dir_path.exists():
            console.print(f"[red]错误: 目录不存在 {directory}[/red]")
            return

        # Find all markdown files
        extensions = self.config.watcher.get('extensions', ['.md', '.markdown'])
        files = []
        for ext in extensions:
            files.extend(dir_path.rglob(f"*{ext}"))

        if not files:
            console.print("[yellow]没有找到markdown文件[/yellow]")
            return

        console.print(f"找到 [bold]{len(files)}[/bold] 个文件\n")

        # Process with progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            task = progress.add_task("[cyan]处理中...", total=len(files))

            results = {"success": 0, "failed": 0, "skipped": 0}

            for file_path in files:
                progress.update(task, description=f"[cyan]处理 {file_path.name}")

                result = processor.process_document(str(file_path), event_type='batch')

                if result['status'] == 'success':
                    results['success'] += 1
                elif result['status'] == 'skipped':
                    results['skipped'] += 1
                else:
                    results['failed'] += 1

                progress.advance(task)

        # Show summary
        console.print("\n[bold]处理完成:[/bold]")
        console.print(f"  ✅ 成功: {results['success']}")
        console.print(f"  ⏭️  跳过: {results['skipped']}")
        console.print(f"  ❌ 失败: {results['failed']}")

    def list_documents(self, limit: int = 20):
        """List all documents."""
        console.clear()
        self.show_banner()
        console.print(f"\n[bold cyan]📚 文档列表[/bold cyan]\n")

        documents = self.db.get_all_documents()[:limit]

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("ID", justify="right", style="dim")
        table.add_column("标题", style="cyan")
        table.add_column("状态", justify="center")
        table.add_column("更新时间", style="dim")

        for doc in documents:
            status_emoji = {
                "completed": "✅",
                "pending": "⏳",
                "failed": "❌"
            }.get(doc["processing_status"], "❓")

            table.add_row(
                str(doc["id"]),
                doc["title"] or "无标题",
                f"{status_emoji} {doc['processing_status']}",
                doc["updated_at"]
            )

        console.print(table)

    def interactive_menu(self):
        """Show interactive menu."""
        while True:
            console.clear()
            self.show_banner()

            console.print("\n[bold cyan]📋 主菜单[/bold cyan]\n")

            table = Table(show_header=False, box=None)
            table.add_column("选项", style="yellow", width=4)
            table.add_column("功能", style="white")

            table.add_row("1", "🔍 搜索文档")
            table.add_row("2", "💬 智能问答")
            table.add_row("3", "📄 处理文档")
            table.add_row("4", "📚 查看文档列表")
            table.add_row("5", "📊 系统状态")
            table.add_row("6", "📤 导出文档")
            table.add_row("0", "🚪 退出")

            console.print(table)

            choice = Prompt.ask("\n选择功能", choices=["0", "1", "2", "3", "4", "5", "6"], default="1")

            if choice == "1":
                self.interactive_search()
            elif choice == "2":
                self.interactive_qa()
            elif choice == "3":
                directory = Prompt.ask("输入目录路径", default="./docs/watched")
                self.process_documents(directory)
            elif choice == "4":
                limit = int(Prompt.ask("显示数量", default="20"))
                self.list_documents(limit)
                Prompt.ask("\n按回车继续")
            elif choice == "5":
                self.show_status()
                Prompt.ask("\n按回车继续")
            elif choice == "6":
                self.export_menu()
            elif choice == "0":
                console.print("\n[green]再见！[/green]")
                break

    def export_menu(self):
        """Export submenu."""
        console.print("\n[bold cyan]📤 导出文档[/bold cyan]\n")

        table = Table(show_header=False, box=None)
        table.add_column("选项", style="yellow", width=4)
        table.add_column("格式", style="white")

        table.add_row("1", "📝 导出为 Obsidian 格式")
        table.add_row("2", "📋 导出为 Notion CSV")
        table.add_row("0", "🔙 返回主菜单")

        console.print(table)

        choice = Prompt.ask("\n选择格式", choices=["0", "1", "2"])

        if choice == "1":
            self.export_to_obsidian()
        elif choice == "2":
            self.export_to_notion()
        elif choice == "0":
            return

    def export_to_obsidian(self):
        """Export to Obsidian format."""
        from src.export.exporters import ObsidianExporter

        output_dir = Prompt.ask("输出目录", default="./exports/obsidian")

        with console.status("[bold green]导出中..."):
            exporter = ObsidianExporter()
            result = exporter.export_all(output_dir)

        console.print(f"\n[green]✅ 成功导出 {result['count']} 个文档到 {output_dir}[/green]")

    def export_to_notion(self):
        """Export to Notion format."""
        from src.export.exporters import NotionExporter

        output_file = Prompt.ask("输出文件", default="./exports/notion_import.csv")

        with console.status("[bold green]导出中..."):
            exporter = NotionExporter()
            result = exporter.export_all(output_file)

        console.print(f"\n[green]✅ 成功导出到 {output_file}[/green]")
        console.print(f"[dim]在Notion中导入CSV文件即可[/dim]")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='知识管理系统 - 增强版CLI')
    parser.add_argument('command', nargs='?', choices=['menu', 'search', 'qa', 'status', 'list'],
                       default='menu', help='命令类型')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互模式')

    args = parser.parse_args()

    cli = EnhancedCLI()

    try:
        if args.command == 'menu' or args.interactive:
            cli.interactive_menu()
        elif args.command == 'search':
            cli.interactive_search()
        elif args.command == 'qa':
            cli.interactive_qa()
        elif args.command == 'status':
            cli.show_status()
        elif args.command == 'list':
            cli.list_documents()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]操作已取消[/yellow]")
    except Exception as e:
        console.print(f"\n[red]错误: {e}[/red]")
        logger.exception("CLI error")


if __name__ == "__main__":
    main()
