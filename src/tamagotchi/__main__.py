"""Entry point: `python -m tamagotchi`."""
from __future__ import annotations

import asyncio
import sys

from rich.console import Console

from . import cli, config, save
from .clock import GameClock
from .config import default_save_path
from .game import GameEngine
from .input import make_reader
from .pet import Pet
from .save import SaveError
from .stages import Stage


def _load_or_create(args) -> tuple[Pet, GameClock, str | None]:
    save_path = args.save_path or default_save_path()
    if args.reset:
        save.delete(save_path)

    summary_msg: str | None = None

    if save_path.exists() and not args.reset:
        try:
            bundle = save.load(save_path)
        except SaveError as exc:
            Console().print(f"[yellow]Warning:[/yellow] {exc} — starting a new pet.")
            pet = Pet(name=args.name or cli.random_name(), stage=Stage.EGG)
            speed = args.speed or config.DEFAULT_SPEED
        else:
            pet = bundle.pet
            # An explicit --speed wins; otherwise inherit the saved speed.
            speed = args.speed or bundle.speed
            clock = GameClock(speed=speed)
            summary = save.catch_up(pet, clock, bundle.saved_at)
            if summary.ticks_simulated > 0:
                summary_msg = summary.describe(pet)
            return pet, clock, summary_msg
    else:
        pet = Pet(name=args.name or cli.random_name(), stage=Stage.EGG)
        speed = args.speed or config.DEFAULT_SPEED

    clock = GameClock(speed=speed)
    return pet, clock, summary_msg


async def _run(args) -> int:
    pet, clock, summary = _load_or_create(args)
    save_path = args.save_path or default_save_path()

    console = Console()
    if summary:
        console.print(summary)
        console.print("[dim]Press any key to continue...[/dim]")

    reader = make_reader()
    engine = GameEngine(
        pet,
        clock,
        save_path,
        ascii_only=args.ascii_only,
    )
    with reader:
        if summary:
            # Wait for any key so the player can read the away-summary before
            # the live UI takes over the screen.
            await reader.next_key()
        await engine.run(reader, console=console)
    console.print("[bold cyan]See you soon![/bold cyan]")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = cli.parse_args(argv)
    try:
        return asyncio.run(_run(args))
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
