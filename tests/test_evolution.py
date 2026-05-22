"""Stage transitions and care-score driven adult-form selection."""
from __future__ import annotations

from tamagotchi import config
from tamagotchi.clock import GameClock
from tamagotchi.pet import Pet
from tamagotchi.stages import AdultForm, Stage, pick_adult_form


def test_pick_adult_form_thresholds():
    # avg = 0.8 -> GOOD
    assert pick_adult_form(care_score=80, age_ticks=100) == AdultForm.GOOD
    # avg = 0.5 -> AVERAGE
    assert pick_adult_form(care_score=50, age_ticks=100) == AdultForm.AVERAGE
    # avg = 0.1 -> BAD
    assert pick_adult_form(care_score=10, age_ticks=100) == AdultForm.BAD
    # avg = exactly 0.7 -> GOOD (>=)
    assert pick_adult_form(care_score=70, age_ticks=100) == AdultForm.GOOD
    # avg = exactly 0.3 -> AVERAGE (>=)
    assert pick_adult_form(care_score=30, age_ticks=100) == AdultForm.AVERAGE


def test_stage_transition_at_exact_tick_count():
    """A well-cared-for pet should transition CHILD -> TEEN at exactly
    STAGE_TICKS['CHILD'] ticks."""
    pet = Pet(name="X", stage=Stage.CHILD)
    pet.hunger = pet.happiness = pet.discipline = pet.health = config.STAT_MAX
    clock = GameClock(speed="fast")
    for _ in range(config.STAGE_TICKS["CHILD"] - 1):
        # Keep the pet alive — without this, decay starves the pet long before
        # it would otherwise transition.
        if pet.hunger < 3:
            pet.feed_meal()
        if pet.happiness < 3:
            pet.play()
        if pet.sick:
            pet.medicate()
        if pet.poops > 0:
            pet.clean()
        pet.apply_tick(clock)
        assert pet.stage == Stage.CHILD, f"died early at age {pet.age_ticks}"
    pet.apply_tick(clock)
    assert pet.stage == Stage.TEEN


def test_teen_to_adult_assigns_form_from_care_score():
    pet = Pet(name="X", stage=Stage.TEEN)
    pet.hunger = pet.happiness = pet.discipline = pet.health = config.STAT_MAX
    pet.care_score = 1000  # very high
    pet.age_ticks = 1000
    clock = GameClock(speed="fast")
    # Keep pet alive while ticking through the entire TEEN duration.
    for _ in range(config.STAGE_TICKS["TEEN"]):
        if pet.hunger < 3:
            pet.feed_meal()
        if pet.happiness < 3:
            pet.play()
        if pet.sick:
            pet.medicate()
        if pet.poops > 0:
            pet.clean()
        pet.apply_tick(clock)
    assert pet.stage == Stage.ADULT
    assert pet.adult_form == AdultForm.GOOD


def test_senior_dies_of_old_age():
    pet = Pet(name="X", stage=Stage.SENIOR)
    pet.hunger = pet.happiness = pet.health = config.STAT_MAX
    pet.stage_ticks = config.STAGE_TICKS["SENIOR"] - 1
    clock = GameClock(speed="fast")
    pet.apply_tick(clock)
    assert pet.is_dead()
