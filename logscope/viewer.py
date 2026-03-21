import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, List, TextIO

from rich.console import Console, Group
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.highlighter import RegexHighlighter
from rich.theme import Theme

from .parser import parse_line, LogEntry

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

class LogScopeHighlighter(RegexHighlighter):
    """Apply style to anything that looks like an IP address, URL, or timestamp."""
    base_style = "logscope."
    highlights = [
        r"(?P<ip>\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b)",
        r"(?P<url>https?://[a-zA-Z0-9./?=#_%:-]+)",
        r"(?P<timestamp>\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)",
        r"(?P<uuid>\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b)",
        r"(?P<email>\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b)",
        r"(?P<path>(?:[a-zA-Z]:|\/)[a-zA-Z0-9._\-\/\\ ]+)",
        r"(?P<status_ok>\b(200|201|204)\b)",
        r"(?P<status_warn>\b(301|302|400|401|403|404)\b)",
        r"(?P<status_err>\b(500|502|503|504)\b)",
        r"(?P<method>\b(GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD)\b)",
    ]


theme = Theme({
    "logscope.ip": "bold green",
    "logscope.url": "underline blue",
    "logscope.timestamp": "cyan",
    "logscope.uuid": "bold magenta",
    "logscope.email": "underline yellow",
    "logscope.path": "dim blue",
    "logscope.status_ok": "bold green",
    "logscope.status_warn": "bold yellow",
    "logscope.status_err": "bold red",
    "logscope.method": "bold cyan",
})

console = Console(theme=theme, highlighter=LogScopeHighlighter())

LEVEL_MAPPING = {
    "TRACE": ("🔍", "dim white"), # gray
    "DEBUG": ("🐛", "bold blue"), # blue
    "INFO": ("🔵", "bold green"), # green
    "NOTICE": ("🔔", "bold cyan"),
    "WARN": ("🟡", "bold yellow"), # yellow
    "ERROR": ("🔴", "bold red"), # red
    "CRITICAL": ("💥", "bold magenta"), # purple
    "ALERT": ("🚨", "bold color(208)"), # orange/alert
    "FATAL": ("💀", "bold dark_red"), # dark red
    "UNKNOWN": ("⚪", "dim white")
}


def format_log(entry: LogEntry, line_number: Optional[int] = None) -> Text:
    """Format a log entry with colors and emojis."""
    icon, style = LEVEL_MAPPING.get(entry.level, LEVEL_MAPPING["UNKNOWN"])
    
    text = Text()
    if line_number is not None:
        text.append(f"{line_number:>4} │ ", style="dim")
        
    text.append(f"{icon} {entry.level:<7} ", style=style)
    text.append(entry.message)
    return text


def get_lines(file: TextIO, follow: bool):
    """Generator that yields lines from a file, optionally tailing it."""
    # yield existing lines
    for line in file:
        if line.strip():
            yield line
            
    if not follow:
        return

    # tailing
    console.print(f"[dim]-- 🔭 Tailing new logs... (Press Ctrl+C to exit) --[/dim]")
    try:
        while True:
            line = file.readline()
            if not line:
                time.sleep(0.1)
                continue
            if line.strip():
                yield line
    except KeyboardInterrupt:
        return


def stream_logs(file: TextIO, follow: bool, level: Optional[str] = None, search: Optional[str] = None, export_html: Optional[Path] = None, show_line_numbers: bool = False, since: Optional[datetime] = None, until: Optional[datetime] = None):
    """Basic console mode: prints directly to stdout, supporting tails."""
    if export_html:
        console.record = True
    
    line_count = 0
    try:
        for line in get_lines(file, follow):
            line_count += 1
            entry = parse_line(line)
            
            # Apply filters
            if level and entry.level != level.upper():
                continue
                
            if search and search.lower() not in line.lower():
                continue
                
            if entry.timestamp:
                if since and entry.timestamp.replace(tzinfo=None) < since.replace(tzinfo=None):
                    continue
                if until and entry.timestamp.replace(tzinfo=None) > until.replace(tzinfo=None):
                    continue
                
            formatted = format_log(entry, line_number=line_count if show_line_numbers else None)
            console.print(formatted)
    finally:
        if export_html:
            console.save_html(str(export_html), clear=False)
            console.print(f"\n[bold green]✅ Logs exported successfully to {export_html}[/bold green]")


def run_dashboard(file: TextIO, follow: bool, level_filter: Optional[str] = None, search_filter: Optional[str] = None, show_line_numbers: bool = False, since: Optional[datetime] = None, until: Optional[datetime] = None):
    """Dashboard mode: Shows a summary stats panel and recent logs layout."""
    
    stats = {
        "FATAL": 0,
        "ALERT": 0,
        "CRITICAL": 0,
        "ERROR": 0,
        "WARN": 0,
        "NOTICE": 0,
        "INFO": 0,
        "DEBUG": 0,
        "TRACE": 0,
        "UNKNOWN": 0
    }
    
    total_processed = 0
    recent_logs: List[Text] = []
    MAX_LOGS = 25 # Number of lines to keep in the scrolling window

    def generate_layout() -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=5),
            Layout(name="body")
        )
        
        # Stats table
        table = Table(show_header=False, expand=True, border_style="dim", box=None)
        table.add_column("C1", justify="center")
        table.add_column("C2", justify="center")
        table.add_column("C3", justify="center")
        table.add_column("C4", justify="center")
        
        table.add_row(
            f"[bold dark_red]💀 Fatal: {stats.get('FATAL', 0)}[/bold dark_red]",
            f"[bold magenta]💥 Critical: {stats.get('CRITICAL', 0)}[/bold magenta]",
            f"[bold red]🔴 Errors: {stats.get('ERROR', 0)}[/bold red]",
            f"[bold yellow]🟡 Warns: {stats.get('WARN', 0)}[/bold yellow]"
        )
        table.add_row(
            f"[bold green]🔵 Info: {stats.get('INFO', 0)}[/bold green]",
            f"[bold blue]🐛 Debug: {stats.get('DEBUG', 0)}[/bold blue]",
            f"[dim white]🔍 Trace: {stats.get('TRACE', 0)}[/dim white]",
            f"[dim white]⚪ Unknown: {stats.get('UNKNOWN', 0)}[/dim white]"
        )
        
        layout["header"].update(Panel(table, title=f"[bold]✨ LogScope Live Dashboard — Total: {total_processed}[/bold]", border_style="cyan"))
        
        # Logs
        log_group = Group(*recent_logs)
        title = "Recent Logs (Auto-highlight enabled)"
        if follow:
            title += " - [blink green]● LIVE[/blink green]"
            
        layout["body"].update(Panel(log_group, title=title))
        
        return layout

    console.clear()
    
    try:
        with Live(generate_layout(), console=console, refresh_per_second=10) as live:
            for line in get_lines(file, follow):
                entry = parse_line(line)
                
                # Apply filters
                if level_filter and entry.level != level_filter.upper():
                    continue
                if search_filter and search_filter.lower() not in line.lower():
                    continue
                    
                if entry.timestamp:
                    if since and entry.timestamp.replace(tzinfo=None) < since.replace(tzinfo=None):
                        continue
                    if until and entry.timestamp.replace(tzinfo=None) > until.replace(tzinfo=None):
                        continue
                    
                # Update stats tally
                total_processed += 1
                entry_level = entry.level if entry.level in stats else "UNKNOWN"
                stats[entry_level] += 1

                formatted = format_log(entry, line_number=total_processed if show_line_numbers else None)
                recent_logs.append(formatted)
                if len(recent_logs) > MAX_LOGS:
                    recent_logs.pop(0)
                    
                live.update(generate_layout())
    except KeyboardInterrupt:
        pass
