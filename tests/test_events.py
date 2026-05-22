"""Random events: poop, sickness, misbehaviour. RNG-seeded for determinism."""
from __future__ import annotations

import random

from tamagotchi import config, events
from tamagotchi.pet import Pet
from tamagotchi.stages import Stage


def test_poop_eventually_appears_after_meal():
    pet = Pet(name="X", stage=Stage.CHILD)
    pet.hunger = pet.happiness = pet.health = config.STAT_MAX
    pet.last_meal_tick = 0
    rng = random.Random(42)
    found_poop = False
    for tick in range(1, 5):
        pet.age_ticks = tick
        events.maybe_fire(pet, rng)
        if pet.poops > 0:
            found_poop = True
            break
    # Probability is 5% per tick; with seed 42 in 4 tries it may or may not
    # fire, so we run many seeds to assert the event *can* trigger.
    if not found_poop:
        for seed in range(200):
            test_pet = Pet(name="X", stage=Stage.CHILD)
            test_pet.hunger = test_pet.happiness = test_pet.health = config.STAT_MAX
            test_pet.last_meal_tick = 0
            r = random.Random(seed)
            for tick in range(1, 5):
                test_pet.age_ticks = tick
                events.maybe_fire(test_pet, r)
            if test_pet.poops > 0:
                found_poop = True
                break
    assert found_poop


def test_events_skipped_when_sleeping_or_egg():
    pet = Pet(name="X", stage=Stage.EGG)
    rng = random.Random(0)
    for _ in range(100):
        events.maybe_fire(pet, rng)
    assert pet.poops == 0 and not pet.sick

    pet = Pet(name="X", stage=Stage.CHILD)
    pet.sleeping = True
    pet.last_meal_tick = 0
    for _ in range(100):
        pet.age_ticks += 1
        events.maybe_fire(pet, rng)
    assert pet.poops == 0


def test_sickness_more_likely_when_dirty():
    """With poops present, sickness probability is 4x baseline."""
    # We just check that, with a generous seed budget, dirty pets get sick
    # before clean ones on a tight tick budget.
    clean_sick = 0
    dirty_sick = 0
    for seed in range(200):
        clean = Pet(name="C", stage=Stage.CHILD)
        clean.hunger = clean.happiness = clean.health = config.STAT_MAX
        dirty = Pet(name="D", stage=Stage.CHILD)
        dirty.hunger = dirty.happiness = dirty.health = config.STAT_MAX
        dirty.poops = 2
        rng = random.Random(seed)
        for tick in range(1, 30):
            clean.age_ticks = tick
            dirty.age_ticks = tick
            events.maybe_fire(clean, rng)
            events.maybe_fire(dirty, rng)
        if clean.sick:
            clean_sick += 1
        if dirty.sick:
            dirty_sick += 1
    assert dirty_sick > clean_sick


def test_misbehave_only_in_child_or_teen():
    rng = random.Random(0)
    for stage in (Stage.BABY, Stage.ADULT, Stage.SENIOR):
        pet = Pet(name="X", stage=stage)
        pet.hunger = pet.happiness = pet.health = config.STAT_MAX
        for _ in range(500):
            pet.age_ticks += 1
            events.maybe_fire(pet, rng)
        assert pet.discipline_pending is False, f"{stage} should not misbehave"
