"""The asyncio game engine: tick, input, and render coroutines."""
from __future__ import annotations

import asyncio
import random
import time
from pathlib import Path

from rich.console import Console
from rich.live import Live

from . import config, events, save, sprites, ui
from .clock import GameClock
from .input import KeyReader
from .pet import Pet
from .stages import Stage


class GameEngine:
    """Holds the live `Pet`, the clock, and dispatches keypresses to actions."""

    def __init__(
        self,
        pet: Pet,
        clock: GameClock,
        save_path: Path,
        *,
        ascii_only: bool = False,
        rng_seed: int | None = None,
    ) -> None:
        self.pet = pet
        self.clock = clock
        self.save_path = save_path
        self.ascii_only = ascii_only
        self._rng = random.Random(rng_seed)
        self._stop = asyncio.Event()
        self._latest_action_msg: str | None = None
        self._last_autosave = time.monotonic()

    # ----------------------------------------------------------------- ticks
    async def _tick_task(self) -> None:
        try:
            while not self._stop.is_set():
                await asyncio.sleep(self.clock.tick_seconds)
                if self._stop.is_set():
                    return
                self.pet.apply_tick(self.clock)
                events.maybe_fire(self.pet, self._rng)
                self.pet.last_tick_at = time.time()
                self._maybe_autosave()
        except asyncio.CancelledError:
            return

    def _maybe_autosave(self) -> None:
        now = time.monotonic()
        if now - self._last_autosave >= config.AUTOSAVE_INTERVAL_SECONDS:
            try:
                save.save(self.pet, self.clock.speed, self.save_path)
            except OSError:
                pass
            self._last_autosave = now

    # ----------------------------------------------------------------- input
    async def _input_task(self, reader: KeyReader) -> None:
        try:
            while not self._stop.is_set():
                key = await reader.next_key()
                self._handle_key(key)
        except asyncio.CancelledError:
            return

    def _handle_key(self, key: str) -> None:
        # Dead-pet flow has its own menu.
        if self.pet.is_dead():
            if key == "n":
                self._new_pet()
            elif key == "q":
                self._stop.set()
            return

        if key == "q":
            self._latest_action_msg = "Saving and quitting..."
            self._stop.set()
        elif key == "f":
            ok = self.pet.feed_meal()
            self._latest_action_msg = "Yum, a meal!" if ok else "Already full."
        elif key == "k":
            ok = self.pet.feed_snack()
            self._latest_action_msg = "Snack time!" if ok else "Can't snack right now."
        elif key == "p":
            ok = self.pet.play()
            self._latest_action_msg = "Wheee!" if ok else "Can't play right now."
        elif key == "c":
            ok = self.pet.clean()
            self._latest_action_msg = "Cleaned up!" if ok else "Nothing to clean."
        elif key == "m":
            ok = self.pet.medicate()
            self._latest_action_msg = "Feeling better." if ok else "Not sick."
        elif key == "d":
            ok = self.pet.discipline_pet()
            self._latest_action_msg = "Be good!" if ok else "Pet didn't deserve that."
        elif key == "l":
            self.pet.toggle_light(self.clock)
            self._latest_action_msg = "Lights " + ("off." if self.pet.sleeping else "on.")
        elif key == "s":
            self._latest_action_msg = (
                f"Age {self.pet.age_ticks}t  Stage {self.pet.stage.value}  "
                f"Care {self.pet.care_score:.1f}  Wt {self.pet.weight}"
            )

    def _new_pet(self) -> None:
        self.pet = Pet(name=self.pet.name, stage=Stage.EGG)
        self._latest_action_msg = "A new egg appears!"

    # ---------------------------------------------------------------- render
    async def _render_task(self, live: Live) -> None:
        try:
            while not self._stop.is_set():
                frame = int(time.monotonic() * 2) % 2
                alert = self._latest_action_msg or ui.derive_alert(self.pet)
                live.update(ui.build_layout(self.pet, frame, alert, ascii_only=self.ascii_only))
                await asyncio.sleep(0.25)
        except asyncio.CancelledError:
            return

    # ----------------------------------------------------------------- main
    async def run(self, reader: KeyReader, console: Console | None = None) -> None:
        console = console or Console()
        # Initial frame so Live has something to show immediately.
        initial = ui.build_layout(
            self.pet,
            0,
            ui.derive_alert(self.pet),
            ascii_only=self.ascii_only,
        )
        with Live(initial, console=console, refresh_per_second=4, screen=True) as live:
            tasks = [
                asyncio.create_task(self._tick_task()),
                asyncio.create_task(self._input_task(reader)),
                asyncio.create_task(self._render_task(live)),
            ]
            try:
                await self._stop.wait()
            finally:
                for t in tasks:
                    t.cancel()
                for t in tasks:
                    try:
                        await t
                    except (asyncio.CancelledError, Exception):
                        pass
        # Final save on graceful quit.
        try:
            save.save(self.pet, self.clock.speed, self.save_path)
        except OSError:
            pass
