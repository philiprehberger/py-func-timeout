# Changelog

## 0.2.0 (2026-04-06)

- Add `retry()` decorator with configurable attempts, delay, and exponential backoff
- Add `timeout_context` context manager for wrapping code blocks with a timeout
- Add comprehensive test suite covering sync/async timeout, fallback, retry, and edge cases

## 0.1.7 (2026-03-31)

- Standardize README to 3-badge format with emoji Support section
- Update CI checkout action to v5 for Node.js 24 compatibility
- Add GitHub issue templates, dependabot config, and PR template
## 0.1.6 (2026-03-22)

- Add pytest and mypy tool configuration to pyproject.toml

## 0.1.5 (2026-03-20)

- Add basic import test

## 0.1.4 (2026-03-18)

- Add Development section to README

## 0.1.1 (2026-03-16)

- Re-release for PyPI publishing

## 0.1.0 (2026-03-15)

- Initial release
- `timeout` decorator for sync and async functions
- Configurable fallback value and exception type
- Sync timeout via daemon threads, async via `asyncio.wait_for`
- Nestable and cross-platform
