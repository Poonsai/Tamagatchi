"""Tick <-> real-time conversion and day/night helpers."""
from __future__ import annotations

from . import config


class GameClock:
    """Pure mapper between ticks, real seconds, and the in-game hour."""

    def __init__(self, speed: str = config.DEFAULT_SPEED) -> None:
        if speed not in config.SPEED_PRESETS:
            raise ValueError(f"Unknown speed: {speed!r}")
        self.speed = speed
        self.tick_seconds = config.SPEED_PRESETS[speed]

    def ticks_for_elapsed(self, elapsed_seconds: float) -> int:
        """How many full ticks fit in `elapsed_seconds`."""
        if elapsed_seconds <= 0:
            return 0
        return int(elapsed_seconds // self.tick_seconds)

    def game_hour(self, age_ticks: int) -> int:
        """The current in-game hour [0, 23] given total ticks alive.

        24 game-hours = `TICKS_PER_GAME_DAY` ticks.
        """
        ticks_per_hour = config.TICKS_PER_GAME_DAY / 24
        return int((age_ticks % config.TICKS_PER_GAME_DAY) / ticks_per_hour)

    def is_night(self, age_ticks: int) -> bool:
        """True if the pet should be asleep based on the in-game hour."""
        hour = self.game_hour(age_ticks)
        return hour >= config.SLEEP_START_HOUR or hour < config.SLEEP_END_HOUR
