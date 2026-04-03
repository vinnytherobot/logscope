# API Reference (Summary)

This page documents the public Python-facing surfaces currently used by LogScope.

## CLI entrypoint

- `logscope.cli:app`
  - Typer app exported as the `logscope` command by Poetry scripts.
  - Command options include filtering (`--level`), search (`--search`, `--regex`), display (`--dashboard`), and export (`--export-html`).

## Parser API

- `logscope.parser.LogEntry`
  - Dataclass with fields:
    - `level`
    - `message`
    - `raw`
    - `timestamp`
    - `service`
    - `trace_id`
    - `span_id`

- `logscope.parser.parse_line(line: str) -> LogEntry`
  - Parses bracket-style logs and JSON logs.
  - Normalizes severities (`WARNING` -> `WARN`, `ERR` -> `ERROR`, `EMERGENCY` -> `FATAL`).

## Viewer API

- `logscope.viewer.stream_logs(...)`
  - Prints formatted lines to terminal and optionally exports HTML.

- `logscope.viewer.run_dashboard(...)`
  - Runs Rich live dashboard with severity counters.

## Theme API

- `logscope.themes.DEFAULT_THEMES`
  - Built-in theme map used by `LogScopeManager`.

## Compatibility notes

- Public CLI behavior should remain stable across patch/minor releases.
- Python callable interfaces are currently lightweight and may evolve; treat as semi-public unless explicitly versioned in release notes.
