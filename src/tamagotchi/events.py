"""Random-event layer: poop, sickness, and misbehaviour.

Kept separate from `Pet.apply_tick` so that the deterministic part of the
simulation can be unit-tested without injecting an RNG, and so the entire
event policy lives in one place.
"""
from __future__ import annotations

import random

from . import config
from .pet import Pet
from .stages import Stage


def maybe_fire(pet: Pet, rng: random.Random) -> None:
    """Roll random events for one tick. Mutates `pet` in place.

    Called once per tick by the game engine, immediately after
    `pet.apply_tick`.
    """
    if pet.is_dead() or pet.stage == Stage.EGG or pet.sleeping:
        return

    # Poop: more likely shortly after eating. last_meal_tick is set by
    # `feed_meal`/`feed_snack`; if there was no meal yet (-1), this is False.
    if (
        pet.last_meal_tick >= 0
        and pet.age_ticks - pet.last_meal_tick <= 4
        and pet.poops < config.POOP_MAX_VISIBLE
    ):
        if rng.random() < config.POOP_PROB_AFTER_MEAL:
            pet.poops += 1
            pet.alerts.append("poop")

    # Sickness: rarer baseline, much worse with poops or starvation.
    if not pet.sick:
        prob = config.SICKNESS_PROB_BASE
        if pet.poops > 0 or pet.hunger <= 0:
            prob *= config.SICKNESS_MULT_DIRTY
        if rng.random() < prob:
            pet.sick = True
            pet.alerts.append("sick")

    # Misbehaviour: only children and teens. Once flagged, it stays until
    # disciplined (or the pet ages out of the stage).
    if pet.stage in (Stage.CHILD, Stage.TEEN) and not pet.discipline_pending:
        if rng.random() < config.MISBEHAVE_PROB:
            pet.discipline_pending = True
            pet.alerts.append("misbehave")
