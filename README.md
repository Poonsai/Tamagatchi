# Tamagotchi

A faithful Tamagotchi clone for the terminal. Hatch an egg, feed it, clean up
after it, play with it, scold it when it misbehaves, and watch what it grows
into. Care well and it becomes a healthy adult; neglect it and... well, you'll
see.

Runs in any terminal (Windows `cmd`, macOS `Terminal`, Linux). Single
dependency: [`rich`](https://github.com/Textualize/rich).

## Install

```bash
pip install -e .
```

For development (tests):

```bash
pip install -e ".[dev]"
```

## Run

```bash
python -m tamagotchi
# or, if scripts are on PATH:
tamagotchi
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--speed {fast,medium,slow,authentic}` | `medium` | How fast time passes. `fast` = 2 s/tick, `authentic` = 10 min/tick. |
| `--save-path PATH` | `~/.tamagotchi/save.json` | Where to read/write the save file. |
| `--reset` | off | Delete the existing save and start a fresh egg. |
| `--ascii-only` | off | Avoid Unicode glyphs (recommended in Windows `cmd` with a default font). |
| `--name NAME` | random | Name for a new pet. |

## Controls

Single-key actions while the game is running:

| Key | Action |
|-----|--------|
| `F` | Feed a meal (fills hunger, adds weight) |
| `K` | Give a snack (small hunger, more weight, hurts care score) |
| `P` | Play (boosts happiness, sheds weight) |
| `C` | Clean up poop |
| `M` | Give medicine (only works when sick) |
| `D` | Discipline (scold when misbehaving) |
| `L` | Toggle the light (put pet to sleep / wake) |
| `S` | Show detailed stats |
| `N` | New pet (only after death) |
| `Q` | Quit and save |

## Game mechanics

- **Stats** (0–4): hunger, happiness, discipline, health, plus weight (5–99).
- **Lifecycle:** egg → baby → child → teen → adult → senior → death.
- **Evolution:** care quality during baby/child/teen determines which of three
  adult forms your pet becomes.
- **Sleep:** in-game day is 24 game-hours; pets sleep at night. Wake them and
  their happiness suffers.
- **Random events:** pets poop, get sick (worse if surrounded by poop or
  starving), and misbehave (children/teens) until disciplined.
- **Death:** prolonged starvation, untreated sickness, or old age. Press `N`
  to hatch a new egg.
- **Persistence:** the game autosaves every 30 seconds and on quit. When you
  come back, the pet has aged based on real elapsed time (capped at 7 days).

## Tests

```bash
pytest
```

## Project layout

```
src/tamagotchi/
    __main__.py   pet.py     stages.py    events.py    sprites.py
    cli.py        ui.py      input.py     save.py      game.py
    config.py     clock.py
tests/
```

Pure-data modules (`pet`, `stages`, `events`, `save`, `clock`) have no UI
imports and are exercised by unit tests. `ui` and `input` are isolated so the
engine can be tested headlessly.
