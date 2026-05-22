"""Render small pixel-art sprites using upper-half-block characters.

Each terminal character cell becomes two vertical pixels:
- top pixel = foreground color (drawn with ``▀`` upper half block)
- bottom pixel = background color (the rest of the cell)

When one pixel is transparent we switch glyphs (``▄`` lower half block) so we
never paint a background color outside the sprite.

This is the standard "retro game in a terminal" trick — at a typical 8:16
character aspect ratio, the rendered sprite looks square.
"""
from __future__ import annotations

from rich.text import Text

# Transparent pixel chars in a sprite grid.
TRANSPARENT = (" ", ".")
UPPER_HALF = "▀"   # ▀
LOWER_HALF = "▄"   # ▄
FULL_BLOCK = "█"   # █


def render(grid: list[str], palette: dict[str, str]) -> Text:
    """Convert a pixel grid into a rich.Text using half-block characters.

    `grid` is a list of equal-length strings; each character indexes
    `palette` to a rich-compatible color string (e.g. ``"bright_magenta"``,
    ``"#ffaaff"``). Characters listed in ``TRANSPARENT`` are skipped.

    Pads to an even row count so the row-pairing works cleanly.
    """
    if not grid:
        return Text()
    width = max(len(row) for row in grid)
    rows = [row.ljust(width) for row in grid]
    if len(rows) % 2 == 1:
        rows.append(" " * width)

    text = Text()
    for y in range(0, len(rows), 2):
        top, bot = rows[y], rows[y + 1]
        for x in range(width):
            t_ch, b_ch = top[x], bot[x]
            t_color = None if t_ch in TRANSPARENT else palette.get(t_ch)
            b_color = None if b_ch in TRANSPARENT else palette.get(b_ch)
            if t_color is None and b_color is None:
                text.append(" ")
            elif t_color is None:
                text.append(LOWER_HALF, style=b_color)
            elif b_color is None:
                text.append(UPPER_HALF, style=t_color)
            elif t_color == b_color:
                text.append(FULL_BLOCK, style=t_color)
            else:
                text.append(UPPER_HALF, style=f"{t_color} on {b_color}")
        if y + 2 < len(rows):
            text.append("\n")
    return text


def center_in(text: Text, target_width: int, target_height: int) -> Text:
    """Pad `text` with blank lines/spaces to occupy a fixed box."""
    lines = text.split("\n")
    height = len(lines)
    width = max((line.cell_len for line in lines), default=0)

    out = Text()
    top_pad = max(0, (target_height - height) // 2)
    bot_pad = max(0, target_height - height - top_pad)
    left_pad = max(0, (target_width - width) // 2)

    for _ in range(top_pad):
        out.append("\n")
    for i, line in enumerate(lines):
        out.append(" " * left_pad)
        out.append_text(line)
        if i < len(lines) - 1 or bot_pad > 0:
            out.append("\n")
    for i in range(bot_pad):
        if i < bot_pad - 1:
            out.append("\n")
    return out
