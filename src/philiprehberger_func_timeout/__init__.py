"""Add a timeout to any function call — sync or async."""

from __future__ import annotations

import asyncio
import builtins
import functools
import threading
from typing import Any, Callable, TypeVar

__all__ = ["timeout", "TimeoutError", "timeout_context", "retry"]

_MISSING: Any = object()
_F = TypeVar("_F", bound=Callable[..., Any])


class TimeoutError(builtins.TimeoutError):  # noqa: A001
    """Raised when a function call exceeds the allowed time.

    Attributes:
        seconds: The timeout duration that was exceeded.
    """

    def __init__(self, seconds: float) -> None:
        self.seconds = seconds
        super().__init__(f"Function call timed out after {seconds}s")


def timeout(
    seconds: float,
    *,
    fallback: Any = _MISSING,
    exception: type[BaseException] = TimeoutError,
) -> Callable[[_F], _F]:
    """Decorator that adds a timeout to any function call.

    Works with both sync and async functions. Sync functions run in a daemon
    thread and are joined with the given timeout. Async functions use
    ``asyncio.wait_for``.

    Args:
        seconds: Maximum number of seconds the function may run.
        fallback: Value to return instead of raising on timeout. When provided,
            the timeout exception is suppressed and this value is returned.
        exception: Exception type to raise on timeout. Defaults to
            :class:`TimeoutError`. The exception is instantiated with
            *seconds* as the sole argument.

    Returns:
        A decorator that wraps the target function with timeout behaviour.

    Example::

        @timeout(2.0)
        def slow() -> str:
            time.sleep(10)
            return "done"

        @timeout(1.5, fallback="default")
        async def fetch(url: str) -> str:
            ...
    """
    if seconds <= 0:
        raise ValueError("seconds must be positive")

    def decorator(fn: _F) -> _F:
        if asyncio.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return await asyncio.wait_for(
                        fn(*args, **kwargs),
                        timeout=seconds,
                    )
                except asyncio.TimeoutError:
                    if fallback is not _MISSING:
                        return fallback
                    raise exception(seconds) from None

            return async_wrapper  # type: ignore[return-value]

        @functools.wraps(fn)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            result: Any = _MISSING
            exc: BaseException | None = None

            def target() -> None:
                nonlocal result, exc
                try:
                    result = fn(*args, **kwargs)
                except BaseException as e:
                    exc = e

            thread = threading.Thread(target=target, daemon=True)
            thread.start()
            thread.join(timeout=seconds)

            if thread.is_alive():
                if fallback is not _MISSING:
                    return fallback
                raise exception(seconds)

            if exc is not None:
                raise exc

            return result

        return sync_wrapper  # type: ignore[return-value]

    return decorator


class timeout_context:
    """Context manager that raises on timeout.

    Works only with sync code. Runs the body in a daemon thread and
    joins with the given timeout.

    Args:
        seconds: Maximum number of seconds the block may run.
        fallback: Value stored in ``.result`` instead of raising on timeout.
        exception: Exception type to raise on timeout.

    Example::

        with timeout_context(2.0) as ctx:
            time.sleep(10)
        # raises TimeoutError after 2 seconds
    """

    def __init__(
        self,
        seconds: float,
        *,
        fallback: Any = _MISSING,
        exception: type[BaseException] = TimeoutError,
    ) -> None:
        if seconds <= 0:
            raise ValueError("seconds must be positive")
        self.seconds = seconds
        self.fallback = fallback
        self.exception = exception
        self.result: Any = _MISSING
        self._exc: BaseException | None = None

    def __enter__(self) -> timeout_context:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> bool:
        return False


def retry(
    attempts: int = 3,
    delay: float = 0.0,
    *,
    backoff: float = 1.0,
    on_error: Callable[[Exception, int], None] | None = None,
) -> Callable[[_F], _F]:
    """Decorator that retries a function on failure.

    Works with both sync and async functions.

    Args:
        attempts: Maximum number of tries (must be >= 1).
        delay: Seconds to wait between retries.
        backoff: Multiplier applied to delay after each retry. Use ``2.0``
            for exponential backoff.
        on_error: Optional callback receiving ``(exception, attempt_number)``.

    Returns:
        A decorator that wraps the target function with retry behaviour.

    Example::

        @retry(attempts=3, delay=1.0, backoff=2.0)
        def fetch(url: str) -> str:
            ...
    """
    if attempts < 1:
        raise ValueError("attempts must be >= 1")

    def decorator(fn: _F) -> _F:
        if asyncio.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                last_exc: Exception | None = None
                current_delay = delay
                for attempt in range(1, attempts + 1):
                    try:
                        return await fn(*args, **kwargs)
                    except Exception as exc:
                        last_exc = exc
                        if on_error is not None:
                            on_error(exc, attempt)
                        if attempt < attempts and current_delay > 0:
                            await asyncio.sleep(current_delay)
                            current_delay *= backoff
                raise last_exc  # type: ignore[misc]

            return async_wrapper  # type: ignore[return-value]

        @functools.wraps(fn)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exc: Exception | None = None
            current_delay = delay
            for attempt in range(1, attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
                    if on_error is not None:
                        on_error(exc, attempt)
                    if attempt < attempts and current_delay > 0:
                        import time as _time
                        _time.sleep(current_delay)
                        current_delay *= backoff
            raise last_exc  # type: ignore[misc]

        return sync_wrapper  # type: ignore[return-value]

    return decorator
