"""Cross-platform non-blocking keyboard input.

Yields single lowercase characters as soon as they're typed, without
requiring Enter. POSIX uses ``cbreak`` mode + ``select``; Windows uses
``msvcrt``.

The reader is an async iterable so the game engine can co-operate with the
tick and render coroutines on a single thread.
"""
from __future__ import annotations

import asyncio
import sys
from abc import ABC, abstractmethod
from typing import Iterator


class KeyReader(ABC):
    """Yield single keypresses asynchronously."""

    @abstractmethod
    async def next_key(self) -> str:
        """Wait for and return the next character (lowercase)."""

    def __enter__(self):  # context manager for terminal setup/restore
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


# --------------------------------------------------------------------- POSIX
class PosixKeyReader(KeyReader):
    def __init__(self) -> None:
        import termios

        self._termios = termios
        self._fd = sys.stdin.fileno()
        self._original_attrs = termios.tcgetattr(self._fd)
        self._poll_interval = 0.05

    def __enter__(self):
        import tty

        tty.setcbreak(self._fd)
        return self

    def __exit__(self, exc_type, exc, tb):
        self._termios.tcsetattr(self._fd, self._termios.TCSADRAIN, self._original_attrs)
        return False

    async def next_key(self) -> str:
        import select

        loop = asyncio.get_running_loop()
        while True:
            ready, _, _ = await loop.run_in_executor(
                None, lambda: select.select([sys.stdin], [], [], self._poll_interval)
            )
            if ready:
                ch = sys.stdin.read(1)
                if not ch:
                    continue
                return ch.lower()


# -------------------------------------------------------------------- Windows
class WindowsKeyReader(KeyReader):
    def __init__(self) -> None:
        import msvcrt  # type: ignore[import]

        self._msvcrt = msvcrt
        self._poll_interval = 0.05

    async def next_key(self) -> str:
        loop = asyncio.get_running_loop()
        while True:
            has_key = await loop.run_in_executor(None, self._msvcrt.kbhit)
            if has_key:
                ch = self._msvcrt.getwch()
                if not ch:
                    continue
                return ch.lower()
            await asyncio.sleep(self._poll_interval)


# --------------------------------------------------------------------- fake
class FakeKeyReader(KeyReader):
    """In-memory reader for tests: pre-loaded with a sequence of keys."""

    def __init__(self, keys: Iterator[str] | list[str] | None = None) -> None:
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        if keys:
            for k in keys:
                self._queue.put_nowait(k.lower())

    def push(self, key: str) -> None:
        self._queue.put_nowait(key.lower())

    async def next_key(self) -> str:
        return await self._queue.get()


def make_reader() -> KeyReader:
    """Pick the right concrete reader for the current platform."""
    if sys.platform.startswith("win"):
        return WindowsKeyReader()
    return PosixKeyReader()
