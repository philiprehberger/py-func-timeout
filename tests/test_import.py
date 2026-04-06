"""Tests for philiprehberger_func_timeout."""

from __future__ import annotations

import asyncio
import time

import pytest

from philiprehberger_func_timeout import TimeoutError, retry, timeout, timeout_context


# --- timeout decorator tests ---


def test_import():
    """Module imports successfully."""
    import philiprehberger_func_timeout
    assert hasattr(philiprehberger_func_timeout, "timeout")


def test_sync_timeout_raises():
    @timeout(0.2)
    def slow() -> str:
        time.sleep(2)
        return "done"

    with pytest.raises(TimeoutError) as exc_info:
        slow()
    assert exc_info.value.seconds == 0.2


def test_sync_no_timeout():
    @timeout(2.0)
    def fast() -> str:
        return "done"

    assert fast() == "done"


def test_sync_fallback():
    @timeout(0.2, fallback="default")
    def slow() -> str:
        time.sleep(2)
        return "done"

    assert slow() == "default"


def test_sync_exception_propagation():
    @timeout(2.0)
    def broken() -> str:
        raise ValueError("oops")

    with pytest.raises(ValueError, match="oops"):
        broken()


def test_custom_exception():
    class MyError(Exception):
        def __init__(self, seconds: float) -> None:
            self.seconds = seconds

    @timeout(0.2, exception=MyError)
    def slow() -> str:
        time.sleep(2)
        return "done"

    with pytest.raises(MyError):
        slow()


def test_async_timeout_raises():
    @timeout(0.2)
    async def slow() -> str:
        await asyncio.sleep(2)
        return "done"

    with pytest.raises(TimeoutError):
        asyncio.run(slow())


def test_async_no_timeout():
    @timeout(2.0)
    async def fast() -> str:
        return "done"

    assert asyncio.run(fast()) == "done"


def test_async_fallback():
    @timeout(0.2, fallback="default")
    async def slow() -> str:
        await asyncio.sleep(2)
        return "done"

    assert asyncio.run(slow()) == "default"


def test_invalid_seconds():
    with pytest.raises(ValueError, match="seconds must be positive"):
        timeout(0)


# --- retry decorator tests ---


def test_retry_succeeds_first_try():
    call_count = 0

    @retry(attempts=3)
    def succeed() -> str:
        nonlocal call_count
        call_count += 1
        return "ok"

    assert succeed() == "ok"
    assert call_count == 1


def test_retry_succeeds_after_failures():
    call_count = 0

    @retry(attempts=3)
    def flaky() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise RuntimeError("fail")
        return "ok"

    assert flaky() == "ok"
    assert call_count == 3


def test_retry_exhausted():
    @retry(attempts=2)
    def always_fail() -> str:
        raise RuntimeError("fail")

    with pytest.raises(RuntimeError, match="fail"):
        always_fail()


def test_retry_on_error_callback():
    errors: list[tuple[Exception, int]] = []

    @retry(attempts=3, on_error=lambda e, a: errors.append((e, a)))
    def flaky() -> str:
        raise RuntimeError("fail")

    with pytest.raises(RuntimeError):
        flaky()

    assert len(errors) == 3
    assert errors[0][1] == 1
    assert errors[2][1] == 3


def test_retry_async():
    call_count = 0

    @retry(attempts=3)
    async def flaky() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise RuntimeError("fail")
        return "ok"

    assert asyncio.run(flaky()) == "ok"
    assert call_count == 2


def test_retry_invalid_attempts():
    with pytest.raises(ValueError, match="attempts must be >= 1"):
        retry(attempts=0)


# --- timeout_context tests ---


def test_timeout_context_import():
    assert timeout_context is not None
