#!/usr/bin/env python3
"""Split a regular-grid sprite sheet and export PNG frames plus a GIF."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sprite", type=Path, help="Input sprite sheet image")
    parser.add_argument("--rows", type=int, required=True)
    parser.add_argument("--cols", type=int, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--name", default="sticker", help="Output filename stem")
    parser.add_argument("--duration", type=int, default=100, help="Milliseconds per frame")
    parser.add_argument("--durations", help="Comma-separated milliseconds, one per frame")
    parser.add_argument("--order", choices=("row", "column"), default="row")
    parser.add_argument("--no-loop", action="store_true", help="Play once instead of looping")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.rows < 1 or args.cols < 1 or args.duration < 1:
        raise SystemExit("rows, cols, and duration must be positive")

    source = Image.open(args.sprite).convert("RGBA")
    if source.width % args.cols or source.height % args.rows:
        raise SystemExit("sprite dimensions must divide evenly by rows and cols")

    fw, fh = source.width // args.cols, source.height // args.rows
    cells = (
        [(row, col) for row in range(args.rows) for col in range(args.cols)]
        if args.order == "row"
        else [(row, col) for col in range(args.cols) for row in range(args.rows)]
    )
    frames = [source.crop((col * fw, row * fh, (col + 1) * fw, (row + 1) * fh)) for row, col in cells]

    durations = [args.duration] * len(frames)
    if args.durations:
        durations = [int(value.strip()) for value in args.durations.split(",")]
        if len(durations) != len(frames) or any(value < 1 for value in durations):
            raise SystemExit("durations must contain one positive value per frame")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for index, frame in enumerate(frames, start=1):
        frame.save(args.output_dir / f"{args.name}-{index:02d}.png")

    frames[0].save(
        args.output_dir / f"{args.name}.gif",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=1 if args.no_loop else 0,
        disposal=2,
        optimize=False,
    )


if __name__ == "__main__":
    main()
