"""ASCII art for every (stage, adult_form, mood) combination.

Each entry maps to a list of frames (one or two). The renderer picks a frame
based on a 2 Hz oscillator so the pet appears to breathe / wiggle.

When `ascii_only=True` is requested at the CLI, callers pass that through to
`pick()` and we drop any Unicode glyphs in favour of a plain ASCII set.
"""
from __future__ import annotations

from .stages import AdultForm, Mood, Stage

# ---------------------------------------------------------------- EGG sprites
_EGG_A = r"""
   _____
  /     \
 | . . . |
 | . . . |
  \_____/
""".strip("\n")

_EGG_B = r"""
   _____
  /     \
 | .   . |
 |  . .  |
  \_____/
""".strip("\n")

# --------------------------------------------------------------- BABY sprites
_BABY_HAPPY_A = r"""
   .---.
  / o o \
 (   ^   )
  \ \_/ /
   '---'
""".strip("\n")

_BABY_HAPPY_B = r"""
   .---.
  / O O \
 (   ^   )
  \ \_/ /
   '---'
""".strip("\n")

_BABY_HUNGRY = r"""
   .---.
  / o o \
 (  ___  )
  \  o  /
   '---'
""".strip("\n")

_BABY_SAD = r"""
   .---.
  / - - \
 (   .   )
  \ /-\ /
   '---'
""".strip("\n")

_BABY_SICK = r"""
   .---.
  / x x \
 (   ~   )
  \ ___ /
   '---'
""".strip("\n")

_BABY_SLEEP = r"""
   .---.    z
  / - - \  z
 (  ___  )Z
  \     /
   '---'
""".strip("\n")

# --------------------------------------------------------------- CHILD sprites
_CHILD_HAPPY_A = r"""
    .-^-.
   /     \
  | o   o |
   \  ^  /
    | u |
    '---'
""".strip("\n")

_CHILD_HAPPY_B = r"""
    .-^-.
   /     \
  | O   O |
   \  ^  /
    | u |
    '---'
""".strip("\n")

_CHILD_HUNGRY = r"""
    .-^-.
   /     \
  | o   o |
   \ ___ /
    |   |
    '---'
""".strip("\n")

_CHILD_SAD = r"""
    .-^-.
   /     \
  | -   - |
   \  .  /
    |/-\|
    '---'
""".strip("\n")

_CHILD_SICK = r"""
    .-^-.
   /  ~  \
  | x   x |
   \  ~  /
    |___|
    '---'
""".strip("\n")

_CHILD_SLEEP = r"""
    .-^-.   z
   /     \ z
  | -   - |Z
   \ ___ /
    |   |
    '---'
""".strip("\n")

# --------------------------------------------------------------- TEEN sprites
_TEEN_HAPPY_A = r"""
     .---.
    /     \
   | * o o*|
   |   v   |
    \ \_/ /
     |   |
     '---'
""".strip("\n")

_TEEN_HAPPY_B = r"""
     .---.
    /     \
   |*o   o*|
   |   v   |
    \ \_/ /
     |   |
     '---'
""".strip("\n")

_TEEN_HUNGRY = r"""
     .---.
    /     \
   | o   o |
   |  ___  |
    \  o  /
     |   |
     '---'
""".strip("\n")

_TEEN_SAD = r"""
     .---.
    /     \
   | -   - |
   |   .   |
    \ /-\ /
     |   |
     '---'
""".strip("\n")

_TEEN_SICK = r"""
     .---.
    / ~~~ \
   | x   x |
   |   ~   |
    \ ___ /
     |   |
     '---'
""".strip("\n")

_TEEN_SLEEP = r"""
     .---.   z
    /     \ z
   | -   - |Z
   |  ___  |
    \     /
     |   |
     '---'
""".strip("\n")

# ----------------------------- ADULT sprites (three forms x several moods) --
_ADULT_GOOD_A = r"""
      .---.
     / *   *\
    | (o) (o)|
    |    v    |
     \  ___  /
      |     |
     /|     |\
      '-----'
""".strip("\n")

_ADULT_GOOD_B = r"""
      .---.
     /*    *\
    | (O) (O)|
    |    v    |
     \  ___  /
      |     |
     /|     |\
      '-----'
""".strip("\n")

_ADULT_AVERAGE_A = r"""
      .---.
     /     \
    |  o o  |
    |   -   |
     \ ___ /
      |   |
     /|   |\
      '---'
""".strip("\n")

_ADULT_AVERAGE_B = r"""
      .---.
     /     \
    |  O O  |
    |   -   |
     \ ___ /
      |   |
     /|   |\
      '---'
""".strip("\n")

_ADULT_BAD_A = r"""
     .-^^^-.
    / x   x \
   |    ~    |
   |   ___   |
    \   v   /
     |     |
    /|     |\
     '-----'
""".strip("\n")

_ADULT_BAD_B = r"""
     .-^^^-.
    / X   X \
   |    ~    |
   |   ___   |
    \   v   /
     |     |
    /|     |\
     '-----'
""".strip("\n")

_ADULT_HUNGRY = r"""
      .---.
     /     \
    |  o o  |
    |  ___  |
     \  o  /
      |   |
     /|   |\
      '---'
""".strip("\n")

_ADULT_SAD = r"""
      .---.
     /     \
    |  - -  |
    |   .   |
     \ /-\ /
      |   |
     /|   |\
      '---'
""".strip("\n")

_ADULT_SICK = r"""
      .---.
     / ~~~ \
    | x   x |
    |   ~   |
     \ ___ /
      |   |
     /|   |\
      '---'
""".strip("\n")

_ADULT_SLEEP = r"""
      .---.    z
     /     \  z
    | -   - | Z
    |  ___  |
     \     /
      |   |
     /|   |\
      '---'
""".strip("\n")

# ---------------------------- SENIOR (looks like adult but stooped, glasses) -
_SENIOR_A = r"""
      .---.
     /     \
    | [o][o]|
    |   _   |
     \ \_/ /
      |   |
     /|   |\
      '---'
""".strip("\n")

_SENIOR_B = r"""
      .---.
     /     \
    | [O][O]|
    |   _   |
     \ \_/ /
      |   |
     /|   |\
      '---'
""".strip("\n")

# ------------------------------------------------------------------- DEAD ----
_GHOST = r"""
     .---.
    /     \
   |  x x  |
    \  _  /
     '---'
      ~ ~
""".strip("\n")

# ----------------------------------------------------------- POOP overlays ---
POOP_GLYPH = "(@)"
POOP_GLYPH_ASCII = "(o)"


def _glyphs_to_ascii(s: str) -> str:
    """Strip any non-ASCII chars that are likely to mis-render on Windows cmd
    default font. Keeps whitespace (newlines, tabs, spaces) so layout survives.
    """
    out = []
    for c in s:
        if c in "\n\r\t" or 32 <= ord(c) < 127:
            out.append(c)
        else:
            out.append("*")
    return "".join(out)


# Master sprite table: (stage, adult_form, mood) -> list of frames.
# Keys not present fall back to (stage, adult_form, Mood.IDLE), then to a
# generic per-stage idle.
_TABLE: dict[tuple[Stage, AdultForm | None, Mood], list[str]] = {
    (Stage.EGG, None, Mood.IDLE): [_EGG_A, _EGG_B],

    (Stage.BABY, None, Mood.HAPPY): [_BABY_HAPPY_A, _BABY_HAPPY_B],
    (Stage.BABY, None, Mood.IDLE): [_BABY_HAPPY_A, _BABY_HAPPY_B],
    (Stage.BABY, None, Mood.HUNGRY): [_BABY_HUNGRY],
    (Stage.BABY, None, Mood.SAD): [_BABY_SAD],
    (Stage.BABY, None, Mood.SICK): [_BABY_SICK],
    (Stage.BABY, None, Mood.SLEEPING): [_BABY_SLEEP],
    (Stage.BABY, None, Mood.POOPING): [_BABY_HAPPY_A],

    (Stage.CHILD, None, Mood.HAPPY): [_CHILD_HAPPY_A, _CHILD_HAPPY_B],
    (Stage.CHILD, None, Mood.IDLE): [_CHILD_HAPPY_A, _CHILD_HAPPY_B],
    (Stage.CHILD, None, Mood.HUNGRY): [_CHILD_HUNGRY],
    (Stage.CHILD, None, Mood.SAD): [_CHILD_SAD],
    (Stage.CHILD, None, Mood.SICK): [_CHILD_SICK],
    (Stage.CHILD, None, Mood.SLEEPING): [_CHILD_SLEEP],
    (Stage.CHILD, None, Mood.POOPING): [_CHILD_HAPPY_A],

    (Stage.TEEN, None, Mood.HAPPY): [_TEEN_HAPPY_A, _TEEN_HAPPY_B],
    (Stage.TEEN, None, Mood.IDLE): [_TEEN_HAPPY_A, _TEEN_HAPPY_B],
    (Stage.TEEN, None, Mood.HUNGRY): [_TEEN_HUNGRY],
    (Stage.TEEN, None, Mood.SAD): [_TEEN_SAD],
    (Stage.TEEN, None, Mood.SICK): [_TEEN_SICK],
    (Stage.TEEN, None, Mood.SLEEPING): [_TEEN_SLEEP],
    (Stage.TEEN, None, Mood.POOPING): [_TEEN_HAPPY_A],

    (Stage.ADULT, AdultForm.GOOD, Mood.HAPPY): [_ADULT_GOOD_A, _ADULT_GOOD_B],
    (Stage.ADULT, AdultForm.GOOD, Mood.IDLE): [_ADULT_GOOD_A, _ADULT_GOOD_B],
    (Stage.ADULT, AdultForm.AVERAGE, Mood.HAPPY): [_ADULT_AVERAGE_A, _ADULT_AVERAGE_B],
    (Stage.ADULT, AdultForm.AVERAGE, Mood.IDLE): [_ADULT_AVERAGE_A, _ADULT_AVERAGE_B],
    (Stage.ADULT, AdultForm.BAD, Mood.HAPPY): [_ADULT_BAD_A, _ADULT_BAD_B],
    (Stage.ADULT, AdultForm.BAD, Mood.IDLE): [_ADULT_BAD_A, _ADULT_BAD_B],

    (Stage.SENIOR, None, Mood.HAPPY): [_SENIOR_A, _SENIOR_B],
    (Stage.SENIOR, None, Mood.IDLE): [_SENIOR_A, _SENIOR_B],

    (Stage.DEAD, None, Mood.DEAD): [_GHOST],
    (Stage.DEAD, None, Mood.IDLE): [_GHOST],
}

# Shared adult fallbacks (regardless of form).
for form in (AdultForm.GOOD, AdultForm.AVERAGE, AdultForm.BAD):
    _TABLE.setdefault((Stage.ADULT, form, Mood.HUNGRY), [_ADULT_HUNGRY])
    _TABLE.setdefault((Stage.ADULT, form, Mood.SAD), [_ADULT_SAD])
    _TABLE.setdefault((Stage.ADULT, form, Mood.SICK), [_ADULT_SICK])
    _TABLE.setdefault((Stage.ADULT, form, Mood.SLEEPING), [_ADULT_SLEEP])
    _TABLE.setdefault((Stage.ADULT, form, Mood.POOPING), _TABLE[(Stage.ADULT, form, Mood.HAPPY)])

# Senior shares adult shapes for non-idle moods.
_TABLE.setdefault((Stage.SENIOR, None, Mood.HUNGRY), [_ADULT_HUNGRY])
_TABLE.setdefault((Stage.SENIOR, None, Mood.SAD), [_ADULT_SAD])
_TABLE.setdefault((Stage.SENIOR, None, Mood.SICK), [_ADULT_SICK])
_TABLE.setdefault((Stage.SENIOR, None, Mood.SLEEPING), [_ADULT_SLEEP])
_TABLE.setdefault((Stage.SENIOR, None, Mood.POOPING), [_SENIOR_A])


def pick(stage: Stage, adult_form: AdultForm | None, mood: Mood, frame: int, ascii_only: bool = False) -> str:
    """Return the sprite string for `(stage, adult_form, mood)` at `frame`.

    Falls back gracefully to the IDLE sprite for the same stage/form, then to
    the EGG sprite if nothing matches (shouldn't happen in normal play).
    """
    key = (stage, adult_form, mood)
    frames = _TABLE.get(key)
    if frames is None:
        frames = _TABLE.get((stage, adult_form, Mood.IDLE))
    if frames is None:
        # Forms-agnostic IDLE for the stage.
        frames = _TABLE.get((stage, None, Mood.IDLE))
    if frames is None:
        frames = _TABLE[(Stage.EGG, None, Mood.IDLE)]
    sprite = frames[frame % len(frames)]
    if ascii_only:
        return _glyphs_to_ascii(sprite)
    return sprite


def mood_color(mood: Mood) -> str:
    """rich-compatible color string for the given mood."""
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
