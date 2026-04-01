# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Added contributor-focused documentation and GitHub templates.
- Added CI/CD workflow definitions for testing, releases, PR checks, and dependency updates.

## [0.2.0] - 2026-03-31

### Added
- Pulse HUD (`--pulse`) with signal deck, throughput, and severity sparkline.
- Minimum severity filtering with `--min-level`.
- JSON observability field extraction (`service`, `trace`, `span`).
- New `spectra` theme.
- Multi-level filter, regex search, invert match, no-color mode, gzip support.

### Fixed
- Windows UTF-8 output compatibility issue.

## [0.1.0] - 2026-03-01

### Added
- Initial public LogScope CLI release.

---

## Changelog update process

- During development, add notes under `[Unreleased]`.
- On release tag (`v*`), `release.yml` can generate release notes and create a GitHub Release.
- Maintainer then moves finalized notes from `[Unreleased]` to a versioned section.
