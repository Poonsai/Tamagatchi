"""UI smoke tests: render a layout without crashing, contain expected strings."""
from __future__ import annotations

from rich.console import Console

from tamagotchi import config
from tamagotchi.pet import Pet
from tamagotchi.stages import AdultForm, Stage
from tamagotchi.ui import build_layout, classify_mood, derive_alert
from tamagotchi.stages import Mood


def _render_text(pet: Pet, alert: str | None = None, ascii_only: bool = False) -> str:
    console = Console(record=True, width=80, force_terminal=True, color_system=None)
    layout = build_layout(pet, frame=0, alert=alert, ascii_only=ascii_only)
    console.print(layout)
    return console.export_text()


def test_layout_renders_for_every_stage():
    """Make sure every stage renders without raising."""
    for stage in (Stage.EGG, Stage.BABY, Stage.CHILD, Stage.TEEN, Stage.SENIOR, Stage.DEAD):
        pet = Pet(name="Test", stage=stage)
        pet.hunger = pet.happiness = pet.discipline = pet.health = config.STAT_MAX
        text = _render_text(pet)
        assert "Stats" in text
        assert "Test" in text or stage == Stage.DEAD


def test_adult_form_appears_in_stats():
    pet = Pet(name="Mochi", stage=Stage.ADULT, adult_form=AdultForm.GOOD)
    pet.hunger = pet.happiness = pet.discipline = pet.health = config.STAT_MAX
    text = _render_text(pet)
    assert "Mametchi" in text


def test_dead_layout_offers_new_pet():
    pet = Pet(name="Zombie", stage=Stage.DEAD)
    text = _render_text(pet)
    assert "Game Over" in text
    assert "[N]" in text


def test_ascii_only_strips_unicode_glyphs():
    pet = Pet(name="Cmd", stage=Stage.ADULT, adult_form=AdultForm.GOOD)
    pet.hunger = pet.happiness = pet.discipline = pet.health = config.STAT_MAX
    text = _render_text(pet, ascii_only=True)
    # No heart characters in ASCII mode (just #/- bars).
    assert "♥" not in text
    assert "★" not in text


def test_classify_mood_priority_order():
    pet = Pet(name="X", stage=Stage.CHILD)
    pet.hunger = pet.happiness = pet.discipline = pet.health = config.STAT_MAX
    assert classify_mood(pet) == Mood.HAPPY

    pet.poops = 1
    assert classify_mood(pet) == Mood.POOPING

    pet.sleeping = True
    assert classify_mood(pet) == Mood.SLEEPING

    pet.sick = True
    # Sick beats everything else (except DEAD).
    assert classify_mood(pet) == Mood.SICK

    pet.stage = Stage.DEAD
    assert classify_mood(pet) == Mood.DEAD


def test_derive_alert_for_healthy_pet_is_quiet():
    pet = Pet(name="X", stage=Stage.CHILD)
    pet.hunger = pet.happiness = pet.discipline = pet.health = config.STAT_MAX
    assert derive_alert(pet) is None


def test_derive_alert_for_hungry_sick_pet():
    pet = Pet(name="X", stage=Stage.CHILD)
    pet.hunger = 1
    pet.happiness = 3
    pet.health = 4
    pet.sick = True
    pet.poops = 2
    msg = derive_alert(pet)
    assert msg is not None
    assert "Sick" in msg
    assert "poop" in msg
    assert "Hungry" in msg
