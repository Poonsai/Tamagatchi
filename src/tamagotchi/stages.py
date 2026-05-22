"""Life-stage enums, evolution thresholds, and mood classification."""
from __future__ import annotations

from enum import Enum

from . import config


class Stage(str, Enum):
    EGG = "EGG"
    BABY = "BABY"
    CHILD = "CHILD"
    TEEN = "TEEN"
    ADULT = "ADULT"
    SENIOR = "SENIOR"
    DEAD = "DEAD"


class AdultForm(str, Enum):
    GOOD = "GOOD"
    AVERAGE = "AVERAGE"
    BAD = "BAD"


# Display names for each adult form. Light homage to the original characters
# without copying them outright.
ADULT_NAMES = {
    AdultForm.GOOD: "Mametchi",
    AdultForm.AVERAGE: "Tarakotchi",
    AdultForm.BAD: "Maskutchi",
}


# Linear progression. SENIOR -> DEAD is handled by `advance` directly.
_NEXT_STAGE = {
    Stage.EGG: Stage.BABY,
    Stage.BABY: Stage.CHILD,
    Stage.CHILD: Stage.TEEN,
    Stage.TEEN: Stage.ADULT,
    Stage.ADULT: Stage.SENIOR,
    Stage.SENIOR: Stage.DEAD,
}


def next_stage(stage: Stage) -> Stage:
    """Return the stage that follows `stage`."""
    return _NEXT_STAGE.get(stage, Stage.DEAD)


def stage_duration(stage: Stage) -> int:
    """Return the duration of `stage` in ticks (0 for DEAD)."""
    if stage == Stage.DEAD:
        return 0
    return config.STAGE_TICKS[stage.value]


def pick_adult_form(care_score: float, age_ticks: int) -> AdultForm:
    """Pick the adult form based on average care score per tick.

    `age_ticks` is the pet's lifetime so far; we normalise the cumulative
    `care_score` by it so the threshold is in [-2.0, 1.0] (matching the
    per-tick contributions in `Pet.apply_tick`).
    """
    if age_ticks <= 0:
        return AdultForm.AVERAGE
    avg = care_score / age_ticks
    if avg >= config.CARE_THRESHOLD_GOOD:
        return AdultForm.GOOD
    if avg >= config.CARE_THRESHOLD_AVERAGE:
        return AdultForm.AVERAGE
    return AdultForm.BAD


class Mood(str, Enum):
    """How the pet visually appears. Highest-priority condition wins."""

    SICK = "SICK"
    SLEEPING = "SLEEPING"
    POOPING = "POOPING"
    HUNGRY = "HUNGRY"
    SAD = "SAD"
    HAPPY = "HAPPY"
    IDLE = "IDLE"
    DEAD = "DEAD"
