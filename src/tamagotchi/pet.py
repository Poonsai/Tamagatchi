"""Pet data model and per-tick simulation.

Everything in this module is pure logic: no IO, no UI, no randomness (random
events live in `events.py`). That keeps the model unit-testable.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field, asdict

from . import config
from .clock import GameClock
from .stages import AdultForm, Stage, next_stage, pick_adult_form, stage_duration


@dataclass
class Pet:
    name: str
    stage: Stage = Stage.EGG
    adult_form: AdultForm | None = None

    hunger: int = 3
    happiness: int = 3
    discipline: int = 3
    health: int = 4
    weight: int = config.WEIGHT_BASELINE["EGG"]

    age_ticks: int = 0
    stage_ticks: int = 0
    care_score: float = 0.0

    sick: bool = False
    poops: int = 0
    sleeping: bool = False
    discipline_pending: bool = False

    # Internal counters reset by certain actions/events; surfaced for save/load.
    starvation_ticks: int = 0
    dying_ticks: int = 0
    snacks_today: int = 0
    last_meal_tick: int = -1

    last_tick_at: float = field(default_factory=time.time)
    alerts: list[str] = field(default_factory=list)

    # ------------------------------------------------------------------ helpers
    def is_dead(self) -> bool:
        return self.stage == Stage.DEAD

    def clamp_stats(self) -> None:
        self.hunger = max(0, min(config.STAT_MAX, self.hunger))
        self.happiness = max(0, min(config.STAT_MAX, self.happiness))
        self.discipline = max(0, min(config.STAT_MAX, self.discipline))
        self.health = max(0, min(config.STAT_MAX, self.health))
        self.weight = max(config.WEIGHT_MIN, min(config.WEIGHT_MAX, self.weight))
        self.poops = max(0, min(config.POOP_MAX_VISIBLE, self.poops))

    # ------------------------------------------------------------------- tick
    def apply_tick(self, clock: GameClock) -> None:
        """Advance the simulation by exactly one tick.

        Decay, sleep handling, care score, and stage transitions live here.
        Random events (poop, sickness, misbehaviour) are layered on top by
        `events.maybe_fire` after this method runs.
        """
        if self.is_dead():
            return

        self.age_ticks += 1
        self.stage_ticks += 1

        # Sleep cycle: pet sleeps automatically at night (skipped during EGG).
        if self.stage == Stage.EGG:
            self.sleeping = False
        else:
            self.sleeping = clock.is_night(self.age_ticks)

        # Reset snack counter at the start of each game-day.
        if self.age_ticks % config.TICKS_PER_GAME_DAY == 0:
            self.snacks_today = 0

        # The egg only counts down to hatching; no other simulation runs.
        if self.stage == Stage.EGG:
            self._maybe_advance_stage()
            return

        decay_factor = 2 if self.sleeping else 1  # sleeping halves decay

        # Hunger.
        hunger_interval = (
            config.HUNGER_DECAY_TICKS_BABY
            if self.stage == Stage.BABY
            else config.HUNGER_DECAY_TICKS
        ) * decay_factor
        if hunger_interval > 0 and self.age_ticks % hunger_interval == 0:
            self.hunger -= 1

        # Happiness.
        happy_interval = config.HAPPINESS_DECAY_TICKS * decay_factor
        if happy_interval > 0 and self.age_ticks % happy_interval == 0:
            self.happiness -= 1

        # Discipline (slow drift downward + extra drop while misbehaving).
        disc_interval = config.DISCIPLINE_DECAY_TICKS * decay_factor
        if disc_interval > 0 and self.age_ticks % disc_interval == 0:
            self.discipline -= 1
        if self.discipline_pending:
            self.discipline = max(0, self.discipline - 1)

        # Weight drifts toward stage baseline.
        baseline = config.WEIGHT_BASELINE[self.stage.value]
        if self.age_ticks % config.WEIGHT_DRIFT_TICKS == 0:
            if self.weight > baseline:
                self.weight -= 1
            elif self.weight < baseline:
                self.weight += 1

        # Starvation hurts health.
        if self.hunger <= 0:
            self.starvation_ticks += 1
            if self.starvation_ticks >= config.STARVATION_HEALTH_TICKS:
                self.health -= 1
                self.starvation_ticks = 0
        else:
            self.starvation_ticks = 0

        # Sickness also degrades health slowly.
        if self.sick and self.age_ticks % 24 == 0:
            self.health -= 1

        self.clamp_stats()

        # Care score: a "good tick" is well-fed, happy, clean, and healthy.
        well_cared = (
            self.hunger >= 2
            and self.happiness >= 2
            and not self.sick
            and self.poops == 0
            and not self.discipline_pending
        )
        if well_cared:
            self.care_score += 1.0
        elif self.hunger <= 0 or self.health <= 0:
            self.care_score -= 2.0
        else:
            # Mildly negative for being unhappy/dirty but not catastrophic.
            self.care_score -= 0.25

        # Death check.
        if self.health <= 0:
            self.dying_ticks += 1
            if self.dying_ticks >= config.DEATH_FROM_HEALTH_TICKS:
                self.stage = Stage.DEAD
                self.alerts.append("died")
                return
        else:
            self.dying_ticks = 0

        # Old age.
        if (
            self.stage == Stage.SENIOR
            and self.stage_ticks >= stage_duration(Stage.SENIOR)
        ):
            self.stage = Stage.DEAD
            self.alerts.append("died_of_old_age")
            return

        self._maybe_advance_stage()

    def _maybe_advance_stage(self) -> None:
        duration = stage_duration(self.stage)
        if duration <= 0:
            return
        if self.stage_ticks < duration:
            return
        prev = self.stage
        self.stage = next_stage(self.stage)
        self.stage_ticks = 0
        # Evolution from TEEN to ADULT branches by care score.
        if prev == Stage.TEEN and self.stage == Stage.ADULT:
            self.adult_form = pick_adult_form(self.care_score, self.age_ticks)
        # Hatching nudges initial stats a bit so the BABY isn't already dying.
        if prev == Stage.EGG and self.stage == Stage.BABY:
            self.hunger = config.STAT_MAX
            self.happiness = config.STAT_MAX
            self.health = config.STAT_MAX
        self.alerts.append(f"stage:{self.stage.value}")

    # ---------------------------------------------------------------- actions
    def feed_meal(self) -> bool:
        """Full meal. Restores hunger, adds weight."""
        if self.is_dead() or self.stage == Stage.EGG or self.sleeping:
            return False
        if self.hunger >= config.STAT_MAX:
            return False
        self.hunger = min(config.STAT_MAX, self.hunger + 2)
        self.weight = min(config.WEIGHT_MAX, self.weight + 2)
        self.last_meal_tick = self.age_ticks
        return True

    def feed_snack(self) -> bool:
        """Snack: small hunger gain, more weight, eventually hurts care score."""
        if self.is_dead() or self.stage == Stage.EGG or self.sleeping:
            return False
        self.hunger = min(config.STAT_MAX, self.hunger + 1)
        self.weight = min(config.WEIGHT_MAX, self.weight + 4)
        self.happiness = min(config.STAT_MAX, self.happiness + 1)
        self.snacks_today += 1
        if self.snacks_today > 3:
            self.care_score -= 1.0
        return True

    def play(self) -> bool:
        if self.is_dead() or self.stage == Stage.EGG or self.sleeping:
            return False
        if self.happiness >= config.STAT_MAX:
            return False
        self.happiness = min(config.STAT_MAX, self.happiness + 2)
        self.weight = max(config.WEIGHT_MIN, self.weight - 1)
        return True

    def clean(self) -> bool:
        if self.is_dead() or self.poops == 0:
            return False
        self.poops = 0
        return True

    def medicate(self) -> bool:
        if self.is_dead() or not self.sick:
            return False
        self.sick = False
        self.health = min(config.STAT_MAX, self.health + 1)
        return True

    def discipline_pet(self) -> bool:
        if self.is_dead() or self.stage == Stage.EGG or self.sleeping:
            return False
        if not self.discipline_pending:
            # Scolding for no reason hurts happiness.
            self.happiness = max(0, self.happiness - 1)
            self.care_score -= 0.5
            return False
        self.discipline_pending = False
        self.discipline = min(config.STAT_MAX, self.discipline + 1)
        return True

    def toggle_light(self, clock: GameClock) -> bool:
        """Manually toggle sleep. If the pet is being woken during night, the
        in-game clock will put it back to sleep on the next tick — that's
        intentional and mirrors the original toy."""
        if self.is_dead() or self.stage == Stage.EGG:
            return False
        self.sleeping = not self.sleeping
        if not clock.is_night(self.age_ticks) and self.sleeping:
            # Forcing sleep during the day is mildly annoying for the pet.
            self.happiness = max(0, self.happiness - 1)
        return True

    # ----------------------------------------------------------- serialisation
    def to_dict(self) -> dict:
        d = asdict(self)
        d["stage"] = self.stage.value
        d["adult_form"] = self.adult_form.value if self.adult_form else None
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        data = dict(data)
        data["stage"] = Stage(data["stage"])
        data["adult_form"] = (
            AdultForm(data["adult_form"]) if data.get("adult_form") else None
        )
        # Keep only fields we know about (forward-compat with extra keys).
        known = {f for f in cls.__dataclass_fields__}
        clean = {k: v for k, v in data.items() if k in known}
        return cls(**clean)
