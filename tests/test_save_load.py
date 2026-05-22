"""JSON save/load round-trip and version error handling."""
from __future__ import annotations

import json

import pytest

from tamagotchi import save
from tamagotchi.pet import Pet
from tamagotchi.save import SaveError
from tamagotchi.stages import AdultForm, Stage


def test_round_trip_equality(tmp_path):
    pet = Pet(
        name="Pippin",
        stage=Stage.ADULT,
        adult_form=AdultForm.GOOD,
        hunger=2,
        happiness=4,
        discipline=3,
        health=4,
        weight=40,
        age_ticks=1234,
        stage_ticks=100,
        care_score=987.5,
        sick=False,
        poops=1,
        sleeping=False,
    )
    path = tmp_path / "save.json"
    save.save(pet, "medium", path)
    bundle = save.load(path)
    # Last-tick timestamp will differ; ignore it.
    bundle.pet.last_tick_at = pet.last_tick_at
    assert bundle.pet == pet
    assert bundle.speed == "medium"


def test_missing_file_raises(tmp_path):
    with pytest.raises(SaveError):
        save.load(tmp_path / "nope.json")


def test_bad_version_raises(tmp_path):
    path = tmp_path / "save.json"
    path.write_text(json.dumps({"version": 99, "pet": {}, "saved_at": 0}))
    with pytest.raises(SaveError):
        save.load(path)


def test_corrupt_json_raises(tmp_path):
    path = tmp_path / "save.json"
    path.write_text("{not valid json")
    with pytest.raises(SaveError):
        save.load(path)


def test_delete_is_idempotent(tmp_path):
    path = tmp_path / "save.json"
    save.delete(path)  # no-op when missing
    path.write_text("{}")
    save.delete(path)
    assert not path.exists()
