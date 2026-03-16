# philiprehberger-func-timeout

[![Tests](https://github.com/philiprehberger/py-func-timeout/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-func-timeout/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-func-timeout.svg)](https://pypi.org/project/philiprehberger-func-timeout/)
[![License](https://img.shields.io/github/license/philiprehberger/py-func-timeout)](LICENSE)

Add a timeout to any function call — sync or async.

## Install

```bash
pip install philiprehberger-func-timeout
```

## Usage

```python
from philiprehberger_func_timeout import timeout
```

### Sync functions

```python
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

## API

| Function / Class | Description |
|------------------|-------------|
| `timeout(seconds, *, fallback, exception)` | Decorator that adds a timeout to sync or async functions |
| `TimeoutError` | Raised on timeout; has a `.seconds` attribute |


## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## License

MIT
