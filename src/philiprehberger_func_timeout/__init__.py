"""Add a timeout to any function call — sync or async."""

from __future__ import annotations

import asyncio
import builtins
import functools
import threading
from typing import Any, Callable, TypeVar

__all__ = ["timeout", "TimeoutError"]

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
