"""Unit tests for Pet stat decay, actions, and death."""
from __future__ import annotations

from tamagotchi import config
from tamagotchi.clock import GameClock
from tamagotchi.pet import Pet
from tamagotchi.stages import Stage


def _hatched_pet(name: str = "T") -> Pet:
    """A pet already past the EGG stage with maxed-out stats, positioned at
    a known waking-hour so decay is deterministic in tests (hour 9 → awake)."""
    return Pet(
        name=name,
        stage=Stage.CHILD,
        hunger=config.STAT_MAX,
        happiness=config.STAT_MAX,
        discipline=config.STAT_MAX,
        health=config.STAT_MAX,
        weight=config.WEIGHT_BASELINE["CHILD"],
        age_ticks=36,        # game-hour 9; firmly inside the awake window
        stage_ticks=0,
    )


def _tick_n(pet: Pet, n: int, clock: GameClock | None = None) -> None:
    clock = clock or GameClock(speed="fast")
    for _ in range(n):
        pet.apply_tick(clock)


def test_hunger_decays_on_schedule():
    pet = _hatched_pet()  # starts at age 36 (game hour 9, awake)
    # 12 ticks later (age 48) hunger should have decayed once. The pet stays
    # awake the whole time (game hours 9 -> 12).
    _tick_n(pet, config.HUNGER_DECAY_TICKS)
    assert pet.hunger == config.STAT_MAX - 1
    assert pet.sleeping is False


def test_egg_does_not_decay_but_advances():
    pet = Pet(name="E", stage=Stage.EGG)
    _tick_n(pet, config.STAGE_TICKS["EGG"])
    # After EGG duration ticks the pet should have hatched.
    assert pet.stage == Stage.BABY
    # Initial hatch resets stats to max so a starving egg doesn't immediately die.
    assert pet.hunger == config.STAT_MAX
    assert pet.health == config.STAT_MAX


def test_feeding_increases_hunger_but_not_above_cap():
    pet = _hatched_pet()
    pet.hunger = 1
    pet.feed_meal()
    assert pet.hunger == 3
    # Already-full should not exceed STAT_MAX.
    pet.hunger = config.STAT_MAX
    assert pet.feed_meal() is False
    assert pet.hunger == config.STAT_MAX


def test_starvation_eventually_kills():
    pet = _hatched_pet()
    pet.hunger = 0
    # Tick until starvation has emptied health, then keep going for the death window.
    clock = GameClock(speed="fast")
    for _ in range(10_000):
        pet.apply_tick(clock)
        if pet.is_dead():
            break
    assert pet.is_dead()


def test_clean_removes_poops():
    pet = _hatched_pet()
    pet.poops = 2
    assert pet.clean() is True
    assert pet.poops == 0
    assert pet.clean() is False  # nothing to clean


def test_medicine_only_works_when_sick():
    pet = _hatched_pet()
    assert pet.medicate() is False
    pet.sick = True
    pet.health = 1
    assert pet.medicate() is True
    assert pet.sick is False
    assert pet.health == 2


def test_discipline_only_works_when_misbehaving():
    pet = _hatched_pet()
    pet.happiness = 3
    # Scolding for no reason hurts happiness, doesn't help discipline.
    assert pet.discipline_pet() is False
    assert pet.happiness == 2
    pet.discipline_pending = True
    pet.discipline = 2
    assert pet.discipline_pet() is True
    assert pet.discipline_pending is False
    assert pet.discipline == 3


def test_actions_blocked_during_sleep():
    pet = _hatched_pet()
    pet.sleeping = True
    pet.hunger = 1
    assert pet.feed_meal() is False
    assert pet.play() is False
    assert pet.hunger == 1
