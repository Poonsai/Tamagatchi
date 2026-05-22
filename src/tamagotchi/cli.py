"""Argument parsing + pet naming."""
from __future__ import annotations

import argparse
import random
from pathlib import Path

from . import config

DEFAULT_NAMES = [
    "Pip", "Bubbles", "Mochi", "Pochi", "Zuzu", "Niko", "Yuki",
    "Kibo", "Tama", "Choco", "Hina", "Sora", "Riku", "Mimi",
]


def random_name(rng: random.Random | None = None) -> str:
    rng = rng or random.Random()
    return rng.choice(DEFAULT_NAMES)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tamagotchi",
        description="A faithful Tamagotchi clone for your terminal.",
    )
    parser.add_argument(
        "--speed",
        choices=sorted(config.SPEED_PRESETS.keys()),
        default=None,
        help=(
            "How fast time passes. If omitted, uses the saved speed when "
            f"resuming, otherwise '{config.DEFAULT_SPEED}'."
        ),
    )
    parser.add_argument(
        "--save-path",
        type=Path,
        default=None,
        help=f"Save file path (default: {config.default_save_path()}).",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete the existing save and start with a fresh egg.",
    )
    parser.add_argument(
        "--ascii-only",
        action="store_true",
        help="Use plain ASCII glyphs (recommended for Windows cmd default font).",
    )
    parser.add_argument(
        "--name",
        default=None,
        help="Name for a new pet (ignored when resuming an existing save).",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)
