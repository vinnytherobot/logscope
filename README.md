# LogScope

LogScope is a Python CLI that parses plain-text and JSON logs and renders them in a readable, filterable, live terminal view.

[![CI](https://github.com/vinnytherobot/logscope/actions/workflows/ci.yml/badge.svg)](https://github.com/vinnytherobot/logscope/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-pytest--cov-informational)](https://github.com/vinnytherobot/logscope/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/logscope)](https://pypi.org/project/logscope/)
[![License](https://img.shields.io/github/license/vinnytherobot/logscope)](./LICENSE)

## Installation

Supported package managers and flows:

```bash
# pip (from PyPI)
pip install logscope

# pip (local editable)
pip install -e .

# Poetry (project contributors)
poetry install
```

## Quickstart

Minimal executable example:

```bash
# 1) Install
pip install logscope

# 2) Run against a file
logscope ./examples/sample.log

# 3) Follow logs in real time with pulse mode
logscope ./examples/docker.log --follow --pulse
```

Useful follow-up commands:

```bash
# Filter by severity
logscope ./examples/api.log --min-level WARN

# Search + regex
logscope ./examples/api.log --search "timeout|refused" --regex

# Export rendered output
logscope ./examples/api.log --export-html report.html
```

## API Reference

Public package entry points:

- `logscope.cli:app` -> Typer command group exposed as `logscope`.
- `logscope.parser.parse_line()` -> parses a single line into `LogEntry`.
- `logscope.viewer.stream_logs()` -> standard stream renderer.
- `logscope.viewer.run_dashboard()` -> dashboard mode renderer.
- `logscope.viewer.run_pulse_stream()` -> pulse mode renderer.

Developer documentation:

- [`docs/architecture-review.md`](./docs/architecture-review.md)
- [`docs/api.md`](./docs/api.md)

## Roadmap

- Stabilize release automation for PyPI publishing and changelog generation.
- Expand test coverage for follow mode and HTML export flows.
- Add user-facing docs for custom theme packs and plugin-like format adapters.

## Contributing

Contribution guide is in [`CONTRIBUTING.md`](./CONTRIBUTING.md).

## License

MIT. See [`LICENSE`](./LICENSE).