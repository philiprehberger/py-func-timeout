# philiprehberger-func-timeout

[![Tests](https://github.com/philiprehberger/py-func-timeout/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-func-timeout/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-func-timeout.svg)](https://pypi.org/project/philiprehberger-func-timeout/)
[![Last updated](https://img.shields.io/github/last-commit/philiprehberger/py-func-timeout)](https://github.com/philiprehberger/py-func-timeout/commits/main)

Add a timeout to any function call, sync or async.

## Installation

```bash
pip install philiprehberger-func-timeout
```

## Usage

```python
from philiprehberger_func_timeout import timeout
import time

@timeout(2.0)
def slow_computation() -> str:
    time.sleep(10)
    return "done"

slow_computation()  # raises TimeoutError after 2 seconds
```

### Async functions

```python
@timeout(1.5)
async def fetch_data(url: str) -> str:
    await asyncio.sleep(10)
    return "data"

await fetch_data("https://example.com")  # raises TimeoutError after 1.5s
```

### Fallback value

```python
@timeout(2.0, fallback="default")
def risky_call() -> str:
    time.sleep(10)
    return "result"

risky_call()  # returns "default" instead of raising
```

### Custom exception

```python
class MyError(Exception):
    def __init__(self, seconds: float) -> None:
        super().__init__(f"Took too long: {seconds}s")

@timeout(3.0, exception=MyError)
def slow() -> None:
    time.sleep(10)
```

### Retry

```python
from philiprehberger_func_timeout import retry

@retry(attempts=3, delay=1.0, backoff=2.0)
def fetch_data(url: str) -> str:
    return requests.get(url).text

result = fetch_data("https://api.example.com/data")
```

## API

| Function / Class | Description |
|------------------|-------------|
| `timeout(seconds, *, fallback, exception)` | Decorator that adds a timeout to sync or async functions |
| `TimeoutError` | Raised on timeout; has a `.seconds` attribute |
| `timeout_context(seconds, *, fallback, exception)` | Context manager that raises on timeout |
| `retry(attempts, delay, *, backoff, on_error)` | Decorator that retries a function on failure with optional backoff |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## Support

If you find this project useful:

⭐ [Star the repo](https://github.com/philiprehberger/py-func-timeout)

🐛 [Report issues](https://github.com/philiprehberger/py-func-timeout/issues?q=is%3Aissue+is%3Aopen+label%3Abug)

💡 [Suggest features](https://github.com/philiprehberger/py-func-timeout/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)

❤️ [Sponsor development](https://github.com/sponsors/philiprehberger)

🌐 [All Open Source Projects](https://philiprehberger.com/open-source-packages)

💻 [GitHub Profile](https://github.com/philiprehberger)

🔗 [LinkedIn Profile](https://www.linkedin.com/in/philiprehberger)

## License

[MIT](LICENSE)
