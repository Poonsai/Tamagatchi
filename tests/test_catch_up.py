"""Offline catch-up: elapsed real time -> simulated ticks, with a cap."""
from __future__ import annotations

from tamagotchi import config, save
from tamagotchi.clock import GameClock
from tamagotchi.pet import Pet
from tamagotchi.stages import Stage


def test_one_hour_at_medium_is_240_ticks():
    pet = Pet(name="X", stage=Stage.CHILD)
    pet.hunger = pet.happiness = pet.discipline = pet.health = config.STAT_MAX
    clock = GameClock(speed="medium")
    saved_at = 1_000_000.0
    summary = save.catch_up(pet, clock, saved_at=saved_at, now=saved_at + 3600)
    # 3600 s / 15 s per tick = 240
    assert summary.ticks_simulated == 240
    assert summary.capped is False


def test_catch_up_caps_at_seven_real_days():
    pet = Pet(name="X", stage=Stage.CHILD)
    pet.hunger = pet.happiness = pet.health = config.STAT_MAX
    clock = GameClock(speed="medium")
    saved_at = 1_000_000.0
    # Pretend a year has passed.
    summary = save.catch_up(pet, clock, saved_at=saved_at, now=saved_at + 365 * 24 * 3600)
    assert summary.capped is True
    assert summary.ticks_simulated == config.MAX_CATCHUP_TICKS


def test_catch_up_with_no_elapsed_time_is_a_no_op():
    pet = Pet(name="X", stage=Stage.CHILD)
    pet.hunger = pet.happiness = pet.discipline = pet.health = config.STAT_MAX
    clock = GameClock(speed="medium")
    saved_at = 1_000_000.0
    summary = save.catch_up(pet, clock, saved_at=saved_at, now=saved_at)
    assert summary.ticks_simulated == 0


def test_catch_up_advances_stage_when_due():
    pet = Pet(name="X", stage=Stage.CHILD)
    pet.hunger = pet.happiness = pet.discipline = pet.health = config.STAT_MAX
    clock = GameClock(speed="medium")
    saved_at = 1_000_000.0
    # Enough seconds to push past the CHILD stage at medium (15s/tick).
    elapsed = (config.STAGE_TICKS["CHILD"] + 1) * 15
    save.catch_up(pet, clock, saved_at=saved_at, now=saved_at + elapsed)
    assert pet.stage in (Stage.TEEN, Stage.ADULT, Stage.SENIOR, Stage.DEAD)
