"""Command line interface for seer-bot."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bot")
    subparsers = parser.add_subparsers(dest="command", required=True)
    parser.add_argument(
        "--config",
        default="config/example.yaml",
        help="Path to configuration file (default: config/example.yaml)",
    )

    init_session = subparsers.add_parser(
        "init-session", help="Initialize a browser session for a profile."
    )
    init_session.add_argument("--profile", required=True, help="Profile name")

    run = subparsers.add_parser("run", help="Run a task for a profile.")
    run.add_argument("--profile", required=True, help="Profile name")
    run.add_argument("--task", required=True, help="Task name")

    debug_network = subparsers.add_parser(
        "debug-network", help="Print xhr/fetch network activity."
    )
    debug_network.add_argument("--profile", required=True, help="Profile name")

    print_config = subparsers.add_parser(
        "print-config", help="Print the resolved profile configuration."
    )
    print_config.add_argument("--profile", required=True, help="Profile name")

    schedule = subparsers.add_parser(
        "schedule", help="Run scheduled tasks for a profile."
    )
    schedule.add_argument("--profile", required=True, help="Profile name")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    from bot.config import load_config, redact_config
    from bot.utils.paths import ensure_profile_dirs

    if hasattr(args, "profile"):
        ensure_profile_dirs(args.profile)

    if args.command == "init-session":
        print(f"init-session stub for profile={args.profile}")
        return 0
    if args.command == "run":
        print(f"run stub for profile={args.profile} task={args.task}")
        return 0
    if args.command == "debug-network":
        print(f"debug-network stub for profile={args.profile}")
        return 0
    if args.command == "print-config":
        config = load_config(Path(args.config))
        profile = config.get_profile(args.profile)
        redacted = redact_config(profile.model_dump())
        print(json.dumps(redacted, ensure_ascii=False, indent=2))
        return 0
    if args.command == "schedule":
        print(f"schedule stub for profile={args.profile}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
