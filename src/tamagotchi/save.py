"""Persistence: atomic JSON save/load + offline catch-up simulation."""
from __future__ import annotations

import json
import os
import random
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from . import config, events
from .clock import GameClock
from .pet import Pet


class SaveError(Exception):
    """Raised when a save file can't be read or is incompatible."""


@dataclass
class SaveBundle:
    pet: Pet
    speed: str
    saved_at: float


def save(pet: Pet, speed: str, path: Path) -> None:
    """Atomically write the save file."""
    pet.last_tick_at = time.time()
    payload = {
        "version": config.SAVE_VERSION,
        "saved_at": pet.last_tick_at,
        "settings": {"speed": speed},
        "pet": pet.to_dict(),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False, suffix=".tmp"
    ) as f:
        json.dump(payload, f, indent=2)
        tmp_path = Path(f.name)
    os.replace(tmp_path, path)


def load(path: Path) -> SaveBundle:
    """Read and validate a save file. Raises SaveError on any problem."""
    if not path.exists():
        raise SaveError(f"No save file at {path}")
    try:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise SaveError(f"Could not read save file: {exc}") from exc

    if payload.get("version") != config.SAVE_VERSION:
        raise SaveError(
            f"Save version {payload.get('version')!r} is incompatible "
            f"(expected {config.SAVE_VERSION})."
        )

    pet_data = payload.get("pet")
    if not isinstance(pet_data, dict):
        raise SaveError("Save file missing 'pet'")
    try:
        pet = Pet.from_dict(pet_data)
    except Exception as exc:  # noqa: BLE001 — propagate as SaveError
        raise SaveError(f"Save file is corrupt: {exc}") from exc

    speed = payload.get("settings", {}).get("speed", config.DEFAULT_SPEED)
    saved_at = float(payload.get("saved_at", time.time()))
    return SaveBundle(pet=pet, speed=speed, saved_at=saved_at)


def delete(path: Path) -> None:
    """Remove the save file if it exists."""
    try:
        path.unlink()
    except FileNotFoundError:
        pass


# ----------------------------------------------------------- catch-up logic
@dataclass
class CatchUpSummary:
    ticks_simulated: int
    elapsed_seconds: float
    capped: bool

    def describe(self, pet: Pet) -> str:
        if self.ticks_simulated <= 0:
            return ""
        minutes = int(self.elapsed_seconds // 60)
        capped_note = " (capped)" if self.capped else ""
        lines = [
            f"While you were away ({minutes} min{capped_note}, "
            f"{self.ticks_simulated} ticks simulated):"
        ]
        if pet.is_dead():
            lines.append(f"  - {pet.name} has passed away. Press N for a new pet.")
            return "\n".join(lines)
        lines.append(f"  - Stage: {pet.stage.value.title()}")
        if pet.poops:
            lines.append(f"  - {pet.poops} poop(s) waiting for you")
        if pet.sick:
            lines.append("  - Your pet got sick!")
        if pet.hunger <= 1:
            lines.append("  - Hungry!")
        if pet.happiness <= 1:
            lines.append("  - Bored/sad")
        if pet.discipline_pending:
            lines.append("  - Misbehaved while you were away")
        return "\n".join(lines)


def catch_up(pet: Pet, clock: GameClock, saved_at: float, now: float | None = None) -> CatchUpSummary:
    """Advance `pet` forward to "now" by simulating ticks.

    Caps at MAX_CATCHUP_TICKS so a pet abandoned for months doesn't hang the
    process — anything beyond the cap simply dies.
    """
    if now is None:
        now = time.time()
    elapsed = max(0.0, now - saved_at)
    n_ticks = clock.ticks_for_elapsed(elapsed)
    capped = False
    if n_ticks > config.MAX_CATCHUP_TICKS:
        n_ticks = config.MAX_CATCHUP_TICKS
        capped = True

    rng = random.Random(int(saved_at * 1000))
    for _ in range(n_ticks):
        if pet.is_dead():
            break
        pet.apply_tick(clock)
        events.maybe_fire(pet, rng)
    pet.last_tick_at = now
    return CatchUpSummary(ticks_simulated=n_ticks, elapsed_seconds=elapsed, capped=capped)
