"""Rich layout builder and mood classification.

The renderer is pure: given a `Pet`, a frame index, and an alert string, it
returns a fully-populated `rich.Layout`. The game engine calls
`build_layout` once per render tick and hands the result to `rich.live.Live`.
"""
from __future__ import annotations

from rich.align import Align
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import sprites
from .pet import Pet
from .stages import ADULT_NAMES, Mood, Stage


# --------------------------------------------------------------------- mood --
def classify_mood(pet: Pet) -> Mood:
    """Pick the visual mood with the highest priority condition winning."""
    if pet.is_dead():
        return Mood.DEAD
    if pet.sick:
        return Mood.SICK
    if pet.sleeping:
        return Mood.SLEEPING
    if pet.poops > 0:
        return Mood.POOPING
    if pet.hunger <= 1:
        return Mood.HUNGRY
    if pet.happiness <= 1 or pet.discipline_pending:
        return Mood.SAD
    if pet.happiness >= 3 and pet.hunger >= 3:
        return Mood.HAPPY
    return Mood.IDLE


# ----------------------------------------------------------------- helpers --
def _stat_bar(label: str, value: int, max_value: int, full_char: str, empty_char: str, color: str) -> Text:
    bar = full_char * value + empty_char * (max_value - value)
    text = Text()
    text.append(f"{label:<11} ", style="bold")
    text.append(bar, style=color)
    text.append(f"  {value}/{max_value}", style="dim")
    return text


def _hearts_bar(label: str, value: int, ascii_only: bool) -> Text:
    if ascii_only:
        return _stat_bar(label, value, 4, "#", "-", "bright_red")
    return _stat_bar(label, value, 4, "♥", "·", "bright_red")


def _moon_bar(label: str, value: int, ascii_only: bool) -> Text:
    if ascii_only:
        return _stat_bar(label, value, 4, "*", "-", "bright_yellow")
    return _stat_bar(label, value, 4, "★", "·", "bright_yellow")


# ----------------------------------------------------------------- panels --
def _sprite_panel(pet: Pet, frame: int, ascii_only: bool) -> Panel:
    mood = classify_mood(pet)
    sprite = sprites.pick(pet.stage, pet.adult_form, mood, frame, ascii_only=ascii_only)
    poop_glyph = sprites.POOP_GLYPH_ASCII if ascii_only else sprites.POOP_GLYPH
    suffix = ""
    if pet.poops > 0 and not pet.is_dead():
        suffix = "  " + " ".join([poop_glyph] * pet.poops)
    text = Text(sprite + suffix, style=sprites.mood_color(mood))
    title = pet.name if not pet.is_dead() else f"{pet.name} (R.I.P.)"
    return Panel(Align.center(text, vertical="middle"), title=title, border_style="cyan")


def _stats_panel(pet: Pet, ascii_only: bool) -> Panel:
    table = Table.grid(padding=(0, 2))
    table.add_column(justify="left")
    table.add_column(justify="left")
    table.add_row(_hearts_bar("Hunger", pet.hunger, ascii_only), _hearts_bar("Happiness", pet.happiness, ascii_only))
    table.add_row(_moon_bar("Discipline", pet.discipline, ascii_only), _hearts_bar("Health", pet.health, ascii_only))

    meta = Text()
    stage_label = pet.stage.value.title()
    if pet.stage == Stage.ADULT and pet.adult_form is not None:
        stage_label = f"{ADULT_NAMES[pet.adult_form]} ({pet.adult_form.value.title()})"
    meta.append(f"Stage: {stage_label}    ", style="bold cyan")
    meta.append(f"Age: {pet.age_ticks} ticks    ", style="dim")
    meta.append(f"Weight: {pet.weight}", style="dim")
    if pet.sick:
        meta.append("    SICK", style="bold green")
    if pet.discipline_pending:
        meta.append("    misbehaving!", style="bold yellow")
    if pet.sleeping:
        meta.append("    zzz", style="grey50")

    layout = Table.grid()
    layout.add_column()
    layout.add_row(table)
    layout.add_row(meta)
    return Panel(layout, title="Stats", border_style="green")


def _menu_panel(pet: Pet) -> Panel:
    if pet.is_dead():
        text = Text()
        text.append("Your pet has passed away.\n\n", style="bold red")
        text.append("[N]", style="bold yellow")
        text.append(" hatch new egg    ", style="white")
        text.append("[Q]", style="bold yellow")
        text.append(" quit", style="white")
        return Panel(text, title="Game Over", border_style="red")

    table = Table.grid(padding=(0, 2), expand=True)
    for _ in range(4):
        table.add_column(justify="left")
    items = [
        ("F", "Feed meal"),
        ("K", "Snack"),
        ("P", "Play"),
        ("C", "Clean"),
        ("M", "Medicine"),
        ("D", "Discipline"),
        ("L", "Light"),
        ("S", "Stats"),
        ("Q", "Quit"),
    ]
    rows: list[list[Text]] = []
    row: list[Text] = []
    for key, label in items:
        cell = Text()
        cell.append(f"[{key}] ", style="bold yellow")
        cell.append(label, style="white")
        row.append(cell)
        if len(row) == 4:
            rows.append(row)
            row = []
    if row:
        while len(row) < 4:
            row.append(Text(""))
        rows.append(row)
    for r in rows:
        table.add_row(*r)
    return Panel(table, title="Actions", border_style="yellow")


def _status_panel(alert: str | None) -> Panel:
    text = Text(alert or "All is well.", style="bold white")
    return Panel(text, border_style="magenta")


def build_layout(pet: Pet, frame: int, alert: str | None = None, ascii_only: bool = False) -> Layout:
    """Build the full live-update layout for the current frame."""
    root = Layout()
    root.split_column(
        Layout(_sprite_panel(pet, frame, ascii_only), name="sprite", ratio=3),
        Layout(_stats_panel(pet, ascii_only), name="stats", size=6),
        Layout(_menu_panel(pet), name="menu", size=5),
        Layout(_status_panel(alert), name="status", size=3),
    )
    return root


def derive_alert(pet: Pet) -> str | None:
    """Plain-text alert string for the status bar."""
    if pet.is_dead():
        return f"{pet.name} has died at age {pet.age_ticks} ticks. Press N for a new pet."
    msgs: list[str] = []
    if pet.sick:
        msgs.append("Sick — give medicine!")
    if pet.discipline_pending:
        msgs.append("Misbehaving — discipline!")
    if pet.poops > 0:
        msgs.append(f"{pet.poops} poop(s) need cleaning")
    if pet.hunger <= 1:
        msgs.append("Hungry!")
    if pet.happiness <= 1:
        msgs.append("Bored / sad")
    if pet.health <= 1:
        msgs.append("Health critical!")
    if not msgs and pet.sleeping:
        return "Sleeping... zzz"
    return " | ".join(msgs) if msgs else None
