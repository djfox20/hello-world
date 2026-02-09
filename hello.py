"""Small test python program."""

from __future__ import annotations

import argparse
from datetime import datetime


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Greet the user with a timestamp.")
    parser.add_argument("--name", default="world", help="Name to greet.")
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="Number of times to print the greeting.",
    )
    parser.add_argument(
        "--uppercase",
        action="store_true",
        help="Uppercase the greeting.",
    )
    return parser


def render_greeting(name: str, now: datetime, uppercase: bool) -> str:
    greeting = f"Hello, {name}! Time: {now:%Y-%m-%d %H:%M:%S}"
    return greeting.upper() if uppercase else greeting


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    now = datetime.now()

    for _ in range(max(args.repeat, 1)):
        print(render_greeting(args.name, now, args.uppercase))


if __name__ == "__main__":
    main()
