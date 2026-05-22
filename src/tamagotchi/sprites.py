"""Pixel-art sprites for every (stage, adult_form, mood) combination.

Each sprite is a 16x16 character grid. Characters are looked up in a per-
sprite palette to assign rich colors, then `pixels.render` collapses each
pair of rows into one terminal cell using upper-half-block characters. The
result is genuinely pixel-art-shaped on screen — at typical terminal cell
aspect ratios (2:1), 16x16 pixel sprites look roughly square.

A small ASCII fallback is kept for `--ascii-only` mode (Windows cmd default
font), reused from the previous implementation.

Character convention inside a sprite grid:
- ``.`` / `` ``  transparent
- ``B``  body main color
- ``L``  body light shade (highlight)
- ``D``  body dark shade (outline / shadow)
- ``e``  eye white / sclera
- ``p``  pupil (black)
- ``m``  mouth / lip
- ``b``  blush
- ``s``  spot / accent
- ``g``  glasses / special accessory
- ``t``  tongue / tear
- ``w``  bright white (ghost outline)
"""
from __future__ import annotations

from rich.text import Text

from . import pixels
from .stages import AdultForm, Mood, Stage

SPRITE_SIZE = 16

# -------------------------------------------------------------- palettes --
# Per-(stage, adult_form) base palettes. Mood may tweak colors at render
# time via `_apply_mood_tint`.

_EGG_PALETTE = {
    "B": "white",
    "L": "grey85",
    "D": "grey50",
    "s": "dark_orange3",
}

_BABY_PALETTE = {
    "B": "deep_sky_blue1",
    "L": "light_sky_blue1",
    "D": "deep_sky_blue4",
    "p": "black",
    "m": "deep_pink3",
    "b": "light_pink1",
    "e": "white",
}

_CHILD_PALETTE = {
    "B": "magenta",
    "L": "light_pink1",
    "D": "deep_pink4",
    "p": "black",
    "m": "deep_pink3",
    "b": "light_pink1",
    "e": "white",
}

_TEEN_PALETTE = {
    "B": "purple",
    "L": "medium_purple",
    "D": "purple4",
    "p": "black",
    "m": "deep_pink3",
    "b": "light_pink1",
    "e": "white",
}

_ADULT_GOOD_PALETTE = {
    "B": "gold1",
    "L": "yellow1",
    "D": "orange3",
    "p": "black",
    "m": "deep_pink3",
    "b": "light_pink1",
    "e": "white",
}

_ADULT_AVERAGE_PALETTE = {
    "B": "tan",
    "L": "wheat1",
    "D": "orange4",
    "p": "black",
    "m": "deep_pink3",
    "b": "light_pink1",
    "e": "white",
}

_ADULT_BAD_PALETTE = {
    "B": "grey50",
    "L": "grey70",
    "D": "grey23",
    "p": "black",
    "m": "deep_pink4",
    "b": "grey39",
    "e": "white",
}

_SENIOR_PALETTE = {
    "B": "grey70",
    "L": "grey85",
    "D": "grey50",
    "p": "black",
    "m": "deep_pink4",
    "g": "grey23",  # glasses frame
    "e": "white",
}

_GHOST_PALETTE = {
    "w": "white",
    "L": "grey78",
    "p": "black",
}

# Mood-driven palette overrides applied on top of the base palette.
_MOOD_OVERRIDE = {
    Mood.SICK:     {"B": "green3", "L": "pale_green1", "D": "dark_green"},
    Mood.SLEEPING: {"B": "grey50", "L": "grey70",      "D": "grey39"},
    Mood.HUNGRY:   {"L": "yellow1"},
    Mood.SAD:      {"L": "deep_sky_blue3"},
    Mood.DEAD:     {},  # ghost has its own palette
}


# ---------------------------------------------------------------- sprites --
# Each sprite is a 16x16 grid. They look hand-pixel-ish on purpose.

# ============================================================== EGG
EGG_A = [
    "................",
    "................",
    "......DDDD......",
    ".....DBBBBD.....",
    "....DBBLLBBD....",
    "...DBBLLLLBBD...",
    "..DBBLsLLLsLBBD.",
    "..DBLLLLLLLLLBD.",
    "..DBLsLLLLLLsLD.",
    "..DBLLLLLsLLLBD.",
    "..DBBLLLLLLLLBD.",
    "...DBBLLLLLLBD..",
    "....DBBLLLLBD...",
    ".....DBBBBBD....",
    "......DDDD......",
    "................",
]

EGG_B = [
    "................",
    "................",
    "......DDDD......",
    ".....DBBBBD.....",
    "....DBBLLBBD....",
    "...DBLsLLLLBBD..",
    "..DBBLLLLLsLBBD.",
    "..DBLLLsLLLLLBD.",
    "..DBLLLLLsLLsBD.",
    "..DBsLLLLLLLLBD.",
    "..DBBLLLsLLLLBD.",
    "...DBBLLLLLLBD..",
    "....DBLsLLLBD...",
    ".....DBBBBBD....",
    "......DDDD......",
    "................",
]

# ============================================================== BABY
BABY_A = [
    "................",
    "................",
    "................",
    ".......DD.......",
    "......DBBD......",
    ".....DBLLBD.....",
    "....DBLLLLBD....",
    "...DBLpLLpLBD...",
    "...DBLLLLLLBD...",
    "...DBbLmmLbBD...",
    "...DBBLLLLBBD...",
    "....DBBBBBBD....",
    ".....DBBBBD.....",
    "......DD.DD.....",
    "................",
    "................",
]

BABY_B = [
    "................",
    "................",
    "................",
    "......DDDD......",
    "......DBBD......",
    ".....DBLLBD.....",
    "....DBLLLLBD....",
    "...DBLpLLpLBD...",
    "...DBLLLLLLBD...",
    "...DBbLmmLbBD...",
    "...DBBLLLLBBD...",
    "....DBBBBBBD....",
    ".....DBBBBD.....",
    "......DDDDD.....",
    "................",
    "................",
]

BABY_SLEEP = [
    "................",
    "................",
    "................",
    "......zDD.......",
    "......DBBD.z....",
    ".....DBLLBDz....",
    "....DBLLLLBD....",
    "...DBL--LL-BD...",
    "...DBLLLLLLBD...",
    "...DBbLLLLbBD...",
    "...DBBLLLLBBD...",
    "....DBBBBBBD....",
    ".....DBBBBD.....",
    "......DDDD......",
    "................",
    "................",
]

BABY_SICK = [
    "................",
    "................",
    "................",
    "......DDDD......",
    "......DBBD......",
    ".....DBLLBD.....",
    "....DBLLLLBD....",
    "...DBpLLLLpBD...",
    "...DBLpLLpLBD...",
    "...DBLLDDLLBD...",
    "...DBBLLLLBBD...",
    "....DBBBBBBD....",
    ".....DBBBBD.....",
    "......DDDD......",
    "................",
    "................",
]

# ============================================================== CHILD
CHILD_A = [
    "................",
    "................",
    "......DDDD......",
    ".....DBBBBD.....",
    "....DBLLLLBD....",
    "...DBLLLLLLBD...",
    "..DBLpeLLepLBD..",
    "..DBLLLLLLLLBD..",
    "..DBLbLmmLbLBD..",
    "..DBLLLLLLLLBD..",
    "...DBBLLLLBBD...",
    "....DBBBBBBD....",
    ".....DBBBBD.....",
    ".....DD..DD.....",
    ".....DD..DD.....",
    "................",
]

CHILD_B = [
    "................",
    "................",
    "......DDDD......",
    ".....DBBBBD.....",
    "....DBLLLLBD....",
    "...DBLLLLLLBD...",
    "..DBLpeLLepLBD..",
    "..DBLLLLLLLLBD..",
    "..DBLbLmmLbLBD..",
    "..DBLLLLLLLLBD..",
    "...DBBLLLLBBD...",
    "....DBBBBBBD....",
    ".....DBBBBD.....",
    "....DDD..DDD....",
    ".....DD..DD.....",
    "................",
]

CHILD_SLEEP = [
    "................",
    "................",
    "......DDDDz.....",
    ".....DBBBBDz....",
    "....DBLLLLBD.z..",
    "...DBLLLLLLBD...",
    "..DBL--LL--LBD..",
    "..DBLLLLLLLLBD..",
    "..DBLLLLLLLLBD..",
    "..DBLLLLLLLLBD..",
    "...DBBLLLLBBD...",
    "....DBBBBBBD....",
    ".....DBBBBD.....",
    ".....DD..DD.....",
    ".....DD..DD.....",
    "................",
]

CHILD_SICK = [
    "................",
    "................",
    "......DDDD......",
    ".....DBBBBD.....",
    "....DBLLLLBD....",
    "...DBLDLLDLBD...",
    "..DBLpDLLDpLBD..",
    "..DBLLDLLDLLBD..",
    "..DBLLLDDLLLBD..",
    "..DBLLDLLDLLBD..",
    "...DBBLLLLBBD...",
    "....DBBBBBBD....",
    ".....DBBBBD.....",
    ".....DD..DD.....",
    ".....DD..DD.....",
    "................",
]

# ============================================================== TEEN
TEEN_A = [
    "................",
    "......DDDD......",
    ".....DBBBBD.....",
    "....DBLLLLBD....",
    "...DBLLLLLLBD...",
    "..DBLpeLLepLBD..",
    "..DBLLLLLLLLBD..",
    ".DBLbLLmmLLbLBD.",
    ".DBLLLLLLLLLLBD.",
    "..DBBLLLLLLBBD..",
    "..DBBBBBBBBBBD..",
    "...DBBBBBBBBD...",
    "....DBBBBBBD....",
    "....DD....DD....",
    "....DD....DD....",
    "................",
]

TEEN_B = [
    "................",
    "......DDDD......",
    ".....DBBBBD.....",
    "....DBLLLLBD....",
    "...DBLLLLLLBD...",
    "..DBLepLLpeLBD..",
    "..DBLLLLLLLLBD..",
    ".DBLbLLmmLLbLBD.",
    ".DBLLLLLLLLLLBD.",
    "..DBBLLLLLLBBD..",
    "..DBBBBBBBBBBD..",
    "...DBBBBBBBBD...",
    "....DBBBBBBD....",
    "...DDD....DDD...",
    "....DD....DD....",
    "................",
]

TEEN_SLEEP = [
    ".............z..",
    "......DDDD..z...",
    ".....DBBBBDz....",
    "....DBLLLLBD....",
    "...DBLLLLLLBD...",
    "..DBL-LLLL-LBD..",
    "..DBLLLLLLLLBD..",
    ".DBLLLLLLLLLLBD.",
    ".DBLLLLLLLLLLBD.",
    "..DBBLLLLLLBBD..",
    "..DBBBBBBBBBBD..",
    "...DBBBBBBBBD...",
    "....DBBBBBBD....",
    "....DD....DD....",
    "....DD....DD....",
    "................",
]

TEEN_SICK = [
    "................",
    "......DDDD......",
    ".....DBBBBD.....",
    "....DBLDDLBD....",
    "...DBLDLLDLBD...",
    "..DBLpDLLDpLBD..",
    "..DBLLLDDLLLBD..",
    ".DBLbLLDDLLbLBD.",
    ".DBLLLLDDLLLLBD.",
    "..DBBLLLLLLBBD..",
    "..DBBBBBBBBBBD..",
    "...DBBBBBBBBD...",
    "....DBBBBBBD....",
    "....DD....DD....",
    "....DD....DD....",
    "................",
]

# ============================================================== ADULT GOOD (Mametchi-like, big eyes, happy)
ADULT_GOOD_A = [
    "................",
    ".....DDDDDD.....",
    "....DBBBBBBD....",
    "...DBLLLLLLBD...",
    "..DBLLLLLLLLBD..",
    "..DBeppLLeppLD..",
    ".DBLpppLLpppLBD.",
    ".DBLLLLbbLLLLBD.",
    ".DBLLLmmmmLLLBD.",
    ".DBLbLLmmLLbLBD.",
    "..DBBLLLLLLBBD..",
    "..DBBBBBBBBBBD..",
    "...DBBBBBBBBD...",
    "...DD......DD...",
    "...DD......DD...",
    "................",
]

ADULT_GOOD_B = [
    "................",
    ".....DDDDDD.....",
    "....DBBBBBBD....",
    "...DBLLLLLLBD...",
    "..DBLLLLLLLLBD..",
    "..DBpppLLpppLD..",
    ".DBLpppLLpppLBD.",
    ".DBLLLLbbLLLLBD.",
    ".DBLLmmmmmmLLBD.",
    ".DBLbLmmmmLbLBD.",
    "..DBBLLLLLLBBD..",
    "..DBBBBBBBBBBD..",
    "...DBBBBBBBBD...",
    "..DDD......DDD..",
    "...DD......DD...",
    "................",
]

# ============================================================== ADULT AVERAGE (plain face)
ADULT_AVERAGE_A = [
    "................",
    ".....DDDDDD.....",
    "....DBBBBBBD....",
    "...DBLLLLLLBD...",
    "..DBLLLLLLLLBD..",
    "..DBLLpLLpLLLD..",
    ".DBLLLLLLLLLLBD.",
    ".DBLLLLLLLLLLBD.",
    ".DBLLLLmmLLLLBD.",
    ".DBLLLLLLLLLLBD.",
    "..DBBLLLLLLBBD..",
    "..DBBBBBBBBBBD..",
    "...DBBBBBBBBD...",
    "...DD......DD...",
    "...DD......DD...",
    "................",
]

ADULT_AVERAGE_B = [
    "................",
    ".....DDDDDD.....",
    "....DBBBBBBD....",
    "...DBLLLLLLBD...",
    "..DBLLLLLLLLBD..",
    "..DBLLpLLpLLLD..",
    ".DBLLLLLLLLLLBD.",
    ".DBLLLLLLLLLLBD.",
    ".DBLLLmmmmLLLBD.",
    ".DBLLLLLLLLLLBD.",
    "..DBBLLLLLLBBD..",
    "..DBBBBBBBBBBD..",
    "...DBBBBBBBBD...",
    "..DDD......DDD..",
    "...DD......DD...",
    "................",
]

# ============================================================== ADULT BAD (grumpy, masked)
ADULT_BAD_A = [
    "................",
    ".....DDDDDD.....",
    "....DBBBBBBD....",
    "...DBLLLLLLBD...",
    "..DBLDDLLDDLBD..",
    "..DBLDpDDpDLLD..",
    ".DBLDDDLLDDDLBD.",
    ".DBLLDLLLLDLLBD.",
    ".DBLLLLDDLLLLBD.",
    ".DBLLLmmmmLLLBD.",
    "..DBBLLLLLLBBD..",
    "..DBBBBBBBBBBD..",
    "...DBBBBBBBBD...",
    "...DD......DD...",
    "...DD......DD...",
    "................",
]

ADULT_BAD_B = [
    "................",
    ".....DDDDDD.....",
    "....DBBBBBBD....",
    "...DBLLLLLLBD...",
    "..DBLDDLLDDLBD..",
    "..DBLDDpDpDDLD..",
    ".DBLDDDLLDDDLBD.",
    ".DBLLDLLLLDLLBD.",
    ".DBLLLLDDLLLLBD.",
    ".DBLLmmmmmmLLBD.",
    "..DBBLLLLLLBBD..",
    "..DBBBBBBBBBBD..",
    "...DBBBBBBBBD...",
    "..DDD......DDD..",
    "...DD......DD...",
    "................",
]

# Adult shared overlays
ADULT_HUNGRY = [
    "................",
    ".....DDDDDD.....",
    "....DBBBBBBD....",
    "...DBLLLLLLBD...",
    "..DBLLLLLLLLBD..",
    "..DBLLpLLpLLLD..",
    ".DBLLLLLLLLLLBD.",
    ".DBLLDDDDDDLLBD.",
    ".DBLLDLLLLDLLBD.",
    ".DBLLDDDDDDLLBD.",
    "..DBBLLLLLLBBD..",
    "..DBBBBBBBBBBD..",
    "...DBBBBBBBBD...",
    "...DD......DD...",
    "...DD......DD...",
    "................",
]

ADULT_SLEEP = [
    "..............z.",
    ".....DDDDDD.z...",
    "....DBBBBBBDz...",
    "...DBLLLLLLBD...",
    "..DBLLLLLLLLBD..",
    "..DBLL-LL-LLLD..",
    ".DBLLLLLLLLLLBD.",
    ".DBLLLLLLLLLLBD.",
    ".DBLLLLLLLLLLBD.",
    ".DBLLLLLLLLLLBD.",
    "..DBBLLLLLLBBD..",
    "..DBBBBBBBBBBD..",
    "...DBBBBBBBBD...",
    "...DD......DD...",
    "...DD......DD...",
    "................",
]

ADULT_SICK = [
    "................",
    ".....DDDDDD.....",
    "....DBBBBBBD....",
    "...DBLDDDDLBD...",
    "..DBLDLLLLDLBD..",
    "..DBLpDLLDpLLD..",
    ".DBLLDDLLDDLLBD.",
    ".DBLLLLDDLLLLBD.",
    ".DBLLLDDDDLLLBD.",
    ".DBLLDDDDDDLLBD.",
    "..DBBLLLLLLBBD..",
    "..DBBBBBBBBBBD..",
    "...DBBBBBBBBD...",
    "...DD......DD...",
    "...DD......DD...",
    "................",
]

ADULT_SAD = [
    "................",
    ".....DDDDDD.....",
    "....DBBBBBBD....",
    "...DBLLLLLLBD...",
    "..DBLLLLLLLLBD..",
    "..DBLLpLLpLLLD..",
    ".DBLLLLLLLLLLBD.",
    ".DBLLLLLLLLLLBD.",
    ".DBLLLmmmmLLLBD.",
    ".DBLLLLLLLLLLBD.",
    ".DBLttLLLLttLBD.",   # tears
    "..DBBLLLLLLBBD..",
    "..DBBBBBBBBBBD..",
    "...DBBBBBBBBD...",
    "...DD......DD...",
    "................",
]

# ============================================================== SENIOR (with glasses)
SENIOR_A = [
    "................",
    ".....DDDDDD.....",
    "....DBBBBBBD....",
    "...DBLLLLLLBD...",
    "..DBLLLLLLLLBD..",
    "..DggggLLggggD..",
    "..DBgpgLLgpgBD..",
    ".DBLggLLLLggLBD.",
    ".DBLLLLLLLLLLBD.",
    ".DBLLLLmmLLLLBD.",
    "..DBBLLLLLLBBD..",
    "..DBBBBBBBBBBD..",
    "...DBBBBBBBBD...",
    "...DD......DD...",
    "...DD......DD...",
    "................",
]

SENIOR_B = [
    "................",
    ".....DDDDDD.....",
    "....DBBBBBBD....",
    "...DBLLLLLLBD...",
    "..DBLLLLLLLLBD..",
    "..DggggLLggggD..",
    "..DBgpgLLgpgBD..",
    ".DBLggLLLLggLBD.",
    ".DBLLLLLLLLLLBD.",
    ".DBLLLmmmmLLLBD.",
    "..DBBLLLLLLBBD..",
    "..DBBBBBBBBBBD..",
    "...DBBBBBBBBD...",
    "..DDD......DDD..",
    "...DD......DD...",
    "................",
]

# ============================================================== DEAD (ghost)
GHOST_A = [
    "................",
    "................",
    "......wwww......",
    ".....wLLLLw.....",
    "....wLLLLLLw....",
    "...wLpLLLLpLw...",
    "...wLLLLLLLLw...",
    "...wLLLmmLLLw...",
    "...wLLLLLLLLw...",
    "..wwLLLLLLLLww..",
    "..wLLLLLLLLLLw..",
    "..wLLLLLLLLLLw..",
    "..wwLwLwwLwLww..",
    "...w.w..w.w.w...",
    "................",
    "................",
]


# ----------------------------------------------------- sprite table --
_SPRITE_TABLE: dict[tuple[Stage, AdultForm | None, Mood], tuple[list[str], dict]] = {
    (Stage.EGG, None, Mood.IDLE):     (EGG_A,    _EGG_PALETTE),

    (Stage.BABY, None, Mood.HAPPY):    (BABY_A,    _BABY_PALETTE),
    (Stage.BABY, None, Mood.IDLE):     (BABY_A,    _BABY_PALETTE),
    (Stage.BABY, None, Mood.HUNGRY):   (BABY_A,    _BABY_PALETTE),
    (Stage.BABY, None, Mood.SAD):      (BABY_A,    _BABY_PALETTE),
    (Stage.BABY, None, Mood.POOPING):  (BABY_A,    _BABY_PALETTE),
    (Stage.BABY, None, Mood.SICK):     (BABY_SICK, _BABY_PALETTE),
    (Stage.BABY, None, Mood.SLEEPING): (BABY_SLEEP,_BABY_PALETTE),

    (Stage.CHILD, None, Mood.HAPPY):    (CHILD_A,    _CHILD_PALETTE),
    (Stage.CHILD, None, Mood.IDLE):     (CHILD_A,    _CHILD_PALETTE),
    (Stage.CHILD, None, Mood.HUNGRY):   (CHILD_A,    _CHILD_PALETTE),
    (Stage.CHILD, None, Mood.SAD):      (CHILD_A,    _CHILD_PALETTE),
    (Stage.CHILD, None, Mood.POOPING):  (CHILD_A,    _CHILD_PALETTE),
    (Stage.CHILD, None, Mood.SICK):     (CHILD_SICK, _CHILD_PALETTE),
    (Stage.CHILD, None, Mood.SLEEPING): (CHILD_SLEEP,_CHILD_PALETTE),

    (Stage.TEEN, None, Mood.HAPPY):    (TEEN_A,    _TEEN_PALETTE),
    (Stage.TEEN, None, Mood.IDLE):     (TEEN_A,    _TEEN_PALETTE),
    (Stage.TEEN, None, Mood.HUNGRY):   (TEEN_A,    _TEEN_PALETTE),
    (Stage.TEEN, None, Mood.SAD):      (TEEN_A,    _TEEN_PALETTE),
    (Stage.TEEN, None, Mood.POOPING):  (TEEN_A,    _TEEN_PALETTE),
    (Stage.TEEN, None, Mood.SICK):     (TEEN_SICK, _TEEN_PALETTE),
    (Stage.TEEN, None, Mood.SLEEPING): (TEEN_SLEEP,_TEEN_PALETTE),

    (Stage.ADULT, AdultForm.GOOD,    Mood.HAPPY):    (ADULT_GOOD_A,    _ADULT_GOOD_PALETTE),
    (Stage.ADULT, AdultForm.GOOD,    Mood.IDLE):     (ADULT_GOOD_A,    _ADULT_GOOD_PALETTE),
    (Stage.ADULT, AdultForm.AVERAGE, Mood.HAPPY):    (ADULT_AVERAGE_A, _ADULT_AVERAGE_PALETTE),
    (Stage.ADULT, AdultForm.AVERAGE, Mood.IDLE):     (ADULT_AVERAGE_A, _ADULT_AVERAGE_PALETTE),
    (Stage.ADULT, AdultForm.BAD,     Mood.HAPPY):    (ADULT_BAD_A,     _ADULT_BAD_PALETTE),
    (Stage.ADULT, AdultForm.BAD,     Mood.IDLE):     (ADULT_BAD_A,     _ADULT_BAD_PALETTE),

    (Stage.SENIOR, None, Mood.HAPPY):    (SENIOR_A, _SENIOR_PALETTE),
    (Stage.SENIOR, None, Mood.IDLE):     (SENIOR_A, _SENIOR_PALETTE),
    (Stage.SENIOR, None, Mood.SLEEPING): (ADULT_SLEEP, _SENIOR_PALETTE),
    (Stage.SENIOR, None, Mood.SICK):     (ADULT_SICK, _SENIOR_PALETTE),
    (Stage.SENIOR, None, Mood.SAD):      (ADULT_SAD, _SENIOR_PALETTE),
    (Stage.SENIOR, None, Mood.HUNGRY):   (ADULT_HUNGRY, _SENIOR_PALETTE),
    (Stage.SENIOR, None, Mood.POOPING):  (SENIOR_A, _SENIOR_PALETTE),

    (Stage.DEAD,  None, Mood.DEAD):  (GHOST_A, _GHOST_PALETTE),
    (Stage.DEAD,  None, Mood.IDLE):  (GHOST_A, _GHOST_PALETTE),
}

# Second-frame variants for animation. If a (stage, form, mood) has a "B"
# variant, the renderer alternates between them.
_FRAME_B = {
    (Stage.EGG,   None, Mood.IDLE):  EGG_B,
    (Stage.BABY,  None, Mood.HAPPY): BABY_B,
    (Stage.BABY,  None, Mood.IDLE):  BABY_B,
    (Stage.CHILD, None, Mood.HAPPY): CHILD_B,
    (Stage.CHILD, None, Mood.IDLE):  CHILD_B,
    (Stage.TEEN,  None, Mood.HAPPY): TEEN_B,
    (Stage.TEEN,  None, Mood.IDLE):  TEEN_B,
    (Stage.ADULT, AdultForm.GOOD,    Mood.HAPPY): ADULT_GOOD_B,
    (Stage.ADULT, AdultForm.GOOD,    Mood.IDLE):  ADULT_GOOD_B,
    (Stage.ADULT, AdultForm.AVERAGE, Mood.HAPPY): ADULT_AVERAGE_B,
    (Stage.ADULT, AdultForm.AVERAGE, Mood.IDLE):  ADULT_AVERAGE_B,
    (Stage.ADULT, AdultForm.BAD,     Mood.HAPPY): ADULT_BAD_B,
    (Stage.ADULT, AdultForm.BAD,     Mood.IDLE):  ADULT_BAD_B,
    (Stage.SENIOR, None, Mood.HAPPY): SENIOR_B,
    (Stage.SENIOR, None, Mood.IDLE):  SENIOR_B,
}

def _palette_for_form(form: AdultForm | None) -> dict:
    if form == AdultForm.GOOD:
        return _ADULT_GOOD_PALETTE
    if form == AdultForm.AVERAGE:
        return _ADULT_AVERAGE_PALETTE
    if form == AdultForm.BAD:
        return _ADULT_BAD_PALETTE
    return _ADULT_AVERAGE_PALETTE


# Adult fallbacks: shared sprite shapes for hungry/sad/sick/sleep but each
# form keeps its own colour palette.
for form in (AdultForm.GOOD, AdultForm.AVERAGE, AdultForm.BAD):
    palette = _palette_for_form(form)
    _SPRITE_TABLE.setdefault((Stage.ADULT, form, Mood.HUNGRY),   (ADULT_HUNGRY, palette))
    _SPRITE_TABLE.setdefault((Stage.ADULT, form, Mood.SAD),      (ADULT_SAD,    palette))
    _SPRITE_TABLE.setdefault((Stage.ADULT, form, Mood.SICK),     (ADULT_SICK,   palette))
    _SPRITE_TABLE.setdefault((Stage.ADULT, form, Mood.SLEEPING), (ADULT_SLEEP,  palette))
    _SPRITE_TABLE.setdefault((Stage.ADULT, form, Mood.POOPING),  _SPRITE_TABLE[(Stage.ADULT, form, Mood.IDLE)])


def _validate_sprite(name: str, grid: list[str]) -> None:
    """Assert that every sprite is 16x16. Catches typos at import time."""
    assert len(grid) == SPRITE_SIZE, f"{name}: expected {SPRITE_SIZE} rows, got {len(grid)}"
    for i, row in enumerate(grid):
        assert len(row) == SPRITE_SIZE, (
            f"{name}: row {i} has {len(row)} chars (expected {SPRITE_SIZE}): {row!r}"
        )


for _name, _grid in dict(globals()).items():
    if _name.isupper() and isinstance(_grid, list) and _grid and isinstance(_grid[0], str) and not _name.startswith("_"):
        _validate_sprite(_name, _grid)


# ----------------------------------------------------- public API --
POOP_GLYPH = "💩"
POOP_GLYPH_ASCII = "(o)"


def _apply_mood_tint(palette: dict, mood: Mood) -> dict:
    """Return a palette adjusted for the current mood (sick=green, etc.)."""
    overrides = _MOOD_OVERRIDE.get(mood, {})
    if not overrides:
        return palette
    return {**palette, **overrides}


def _lookup(stage: Stage, adult_form: AdultForm | None, mood: Mood, frame: int) -> tuple[list[str], dict]:
    """Resolve a sprite for the requested state, with sensible fallbacks."""
    key = (stage, adult_form, mood)
    entry = _SPRITE_TABLE.get(key)
    if entry is None:
        entry = _SPRITE_TABLE.get((stage, adult_form, Mood.IDLE))
    if entry is None:
        entry = _SPRITE_TABLE.get((stage, None, Mood.IDLE))
    if entry is None:
        entry = _SPRITE_TABLE[(Stage.EGG, None, Mood.IDLE)]
    grid, palette = entry
    # Honor frame-B variants only for the (HAPPY/IDLE) sprites that have them.
    if frame % 2 == 1:
        alt = _FRAME_B.get(key) or _FRAME_B.get((stage, adult_form, Mood.IDLE))
        if alt is not None:
            grid = alt
    return grid, palette


def pick(
    stage: Stage,
    adult_form: AdultForm | None,
    mood: Mood,
    frame: int,
    ascii_only: bool = False,
) -> Text:
    """Return a rich.Text sprite for the requested state.

    When `ascii_only=True`, returns a plain-character fallback using a single
    color (still wrapped in Text for a uniform return type).
    """
    if ascii_only:
        return _ascii_fallback(stage, adult_form, mood, frame)
    grid, palette = _lookup(stage, adult_form, mood, frame)
    palette = _apply_mood_tint(palette, mood)
    return pixels.render(grid, palette)


def mood_color(mood: Mood) -> str:
    """Background tint used elsewhere in the UI (alerts, status, etc.)."""
    return {
        Mood.HAPPY: "bright_magenta",
        Mood.IDLE: "white",
        Mood.HUNGRY: "yellow",
        Mood.SAD: "blue",
        Mood.SICK: "green",
        Mood.SLEEPING: "grey50",
        Mood.POOPING: "dark_orange3",
        Mood.DEAD: "grey39",
    }[mood]


# ============================================================ ASCII fallback
# Small, recognizable shapes for `--ascii-only` mode. Reused from the
# previous implementation but condensed to one frame per stage.

_ASCII_FALLBACK: dict[Stage, str] = {
    Stage.EGG: r"""
   _____
  /     \
 | . . . |
 | . . . |
  \_____/
""".strip("\n"),
    Stage.BABY: r"""
   .---.
  / o o \
 (   ^   )
  \ \_/ /
   '---'
""".strip("\n"),
    Stage.CHILD: r"""
    .-^-.
   /     \
  | o   o |
   \  v  /
    | u |
    '---'
""".strip("\n"),
    Stage.TEEN: r"""
     .---.
    /     \
   | * o o*|
   |   v   |
    \ \_/ /
     |   |
     '---'
""".strip("\n"),
    Stage.ADULT: r"""
      .---.
     /     \
    | (o)(o)|
    |   v   |
     \ ___ /
      |   |
     /|   |\
      '---'
""".strip("\n"),
    Stage.SENIOR: r"""
      .---.
     /     \
    | [o][o]|
    |   _   |
     \ \_/ /
      |   |
     /|   |\
      '---'
""".strip("\n"),
    Stage.DEAD: r"""
     .---.
    /     \
   |  x x  |
    \  _  /
     '---'
      ~ ~
""".strip("\n"),
}


def _ascii_fallback(stage: Stage, adult_form: AdultForm | None, mood: Mood, frame: int) -> Text:
    art = _ASCII_FALLBACK.get(stage, _ASCII_FALLBACK[Stage.EGG])
    style = mood_color(mood)
    return Text(art, style=style)
