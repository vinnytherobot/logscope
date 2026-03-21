import sys
import typer
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from typing_extensions import Annotated
from .viewer import stream_logs, run_dashboard

app = typer.Typer(
    help="LogScope — Beautiful log viewer for the terminal",
    add_completion=False,
    rich_markup_mode="rich"
)

def parse_relative_time(time_str: str) -> Optional[datetime]:
    """Parse relative time like '10m', '1h', '2d' or ISO strings."""
    if not time_str:
        return None

    # Check if absolute ISO format first
    try:
        return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
    except ValueError:
        pass

    # Regex for relative formats: <digit><unit>
    match = re.match(r'^(\d+)([smhd])$', time_str.lower())
    if not match:
        return None

    value, unit = int(match.group(1)), match.group(2)
    now = datetime.now()

    if unit == 's': return now - timedelta(seconds=value)
    if unit == 'm': return now - timedelta(minutes=value)
    if unit == 'h': return now - timedelta(hours=value)
    if unit == 'd': return now - timedelta(days=value)

    return None

@app.command()
def main(
    log_file: Annotated[Optional[Path], typer.Argument(help="Path to the log file (leave empty to read from STDIN via pipe)")] = None,
    follow: Annotated[bool, typer.Option("--follow", "-f", help="Follow log output in real-time (like tail -f)")] = False,
    level: Annotated[Optional[str], typer.Option("--level", "-l", help="Filter logs by level (e.g. ERROR, WARNING, INFO)")] = None,
    search: Annotated[Optional[str], typer.Option("--search", "-s", help="Search string to filter logs")] = None,
    dashboard: Annotated[bool, typer.Option("--dashboard", "-d", help="Open visual dashboard showing log statistics")] = False,
    export_html: Annotated[Optional[Path], typer.Option("--export-html", help="Export the beautiful log output to an HTML file")] = None,
    line_numbers: Annotated[bool, typer.Option("--line-numbers", "-n", help="Show line numbers for each log message")] = False,
    since: Annotated[Optional[str], typer.Option("--since", help="Show logs since a point in time (e.g. '1h', '30m', '2026-01-01T00:00:00')")] = None,
    until: Annotated[Optional[str], typer.Option("--until", help="Show logs until a point in time")] = None,
):
    """
    [blue]LogScope[/blue] parses standard logs and makes them [bold]beautiful[/bold] and [bold]readable[/bold].
    """
    if log_file is None:
        if sys.stdin.isatty():
            typer.echo("❌ Error: Please provide a log file path or pipe data to STDIN (cat file | logscope).", err=True)
            raise typer.Exit(1)
        file_obj = sys.stdin
    else:
        file_obj = open(log_file, "r", encoding="utf-8", errors="replace")

    since_dt = parse_relative_time(since) if since else None
    until_dt = parse_relative_time(until) if until else None

    try:
        if dashboard:
            run_dashboard(file_obj, follow=follow, level_filter=level, search_filter=search, show_line_numbers=line_numbers, since=since_dt, until=until_dt)
        else:
            stream_logs(file_obj, follow=follow, level=level, search=search, export_html=export_html, show_line_numbers=line_numbers, since=since_dt, until=until_dt)
    finally:
        if log_file is not None:
            file_obj.close()

if __name__ == "__main__":
    app()
