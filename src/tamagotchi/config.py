"""Centralised game tuning constants.

All numbers here are at "medium" speed. The speed preset only changes the
real-time duration of one tick; everything else (decay intervals, stage
lengths, event probabilities) is measured in ticks so the gameplay is
identical at every speed setting.
"""
from __future__ import annotations

import os
from pathlib import Path

# Real seconds per tick for each speed preset.
SPEED_PRESETS: dict[str, float] = {
    "fast": 2.0,
    "medium": 15.0,
    "slow": 60.0,
    "authentic": 600.0,
}
DEFAULT_SPEED = "medium"

# Stat caps.
STAT_MAX = 4              # hunger, happiness, discipline, health
WEIGHT_MIN = 5
WEIGHT_MAX = 99

# Decay intervals (ticks per -1).
HUNGER_DECAY_TICKS = 12
HUNGER_DECAY_TICKS_BABY = 6
HAPPINESS_DECAY_TICKS = 16
DISCIPLINE_DECAY_TICKS = 48
WEIGHT_DRIFT_TICKS = 24
STARVATION_HEALTH_TICKS = 8   # ticks at hunger=0 before health drops
DEATH_FROM_HEALTH_TICKS = 12  # ticks at health=0 before death

# Sleep cycle: a game day is 96 ticks; sleep window is hours 20:00-08:00.
TICKS_PER_GAME_DAY = 96
SLEEP_START_HOUR = 20
SLEEP_END_HOUR = 8

# Stage durations in ticks. Tweaked so a "fast" playthrough (~2s/tick) covers
# the full lifecycle in roughly two real hours.
STAGE_TICKS = {
    "EGG": 20,
    "BABY": 96,
    "CHILD": 288,
    "TEEN": 480,
    "ADULT": 1920,
    "SENIOR": 960,
}

# Care score thresholds at TEEN -> ADULT.
CARE_THRESHOLD_GOOD = 0.7
CARE_THRESHOLD_AVERAGE = 0.3

# Weight baseline per stage (drift target).
WEIGHT_BASELINE = {
    "EGG": 5,
    "BABY": 15,
    "CHILD": 25,
    "TEEN": 35,
    "ADULT": 45,
    "SENIOR": 50,
    "DEAD": 0,
}

# Event probabilities per tick (multiplied by modifiers in events.py).
POOP_PROB_AFTER_MEAL = 0.05
POOP_MAX_VISIBLE = 2
SICKNESS_PROB_BASE = 0.005
SICKNESS_MULT_DIRTY = 4.0   # multiplier when there are poops or starvation
MISBEHAVE_PROB = 0.01       # CHILD/TEEN only

# Save catch-up cap: don't simulate more than this many ticks at once.
# Anything longer just dies and shows the death screen.
MAX_CATCHUP_TICKS = 7 * 24 * 60 * 60 // int(SPEED_PRESETS["medium"])  # 7 days @ medium

# Autosave cadence (real seconds).
AUTOSAVE_INTERVAL_SECONDS = 30.0

SAVE_VERSION = 1


def default_save_path() -> Path:
    """Pick the save file path.

    Honours `$TAMAGOTCHI_SAVE` for tests and power users; falls back to
    `~/.tamagotchi/save.json`.
    """
    override = os.environ.get("TAMAGOTCHI_SAVE")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".tamagotchi" / "save.json"
