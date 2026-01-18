"""Command line interface for seer-bot."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bot")
    subparsers = parser.add_subparsers(dest="command", required=True)
    parser.add_argument(
        "--config",
        default="config/example.yaml",
        help="Path to configuration file (default: config/example.yaml)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (default: INFO)",
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

    smoke = subparsers.add_parser("smoke", help="Open start_url briefly and exit.")
    smoke.add_argument("--profile", required=True, help="Profile name")

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
    from bot.browser import close_context, create_context
    from bot.runner import run_task
    from bot.utils.logging import log_event, setup_logging
    from bot.utils.paths import ensure_profile_dirs, logs_dir
    from bot.utils.paths import ensure_profile_dirs
    from bot.utils.paths import state_dir

    if hasattr(args, "profile"):
        ensure_profile_dirs(args.profile)
        config = load_config(Path(args.config))
        profile = config.get_profile(args.profile)
        logger = setup_logging(logs_dir() / "run.jsonl", level=args.log_level)
        log_event(logger, "command_start", profile=args.profile, step=args.command)

    if args.command == "init-session":
        session_profile = profile.model_copy(update={"headless": False})
        playwright = browser = context = None
        try:
            playwright, browser, context = create_context(session_profile)
            page = context.new_page()
            page.goto(profile.start_url)
            input("Please log in manually, then press Enter to continue...")
            state_path = state_dir(args.profile) / "storage_state.json"
            context.storage_state(path=str(state_path))
            print(f"Storage state saved to {state_path}")
            return 0
        finally:
            if context and browser and playwright:
                close_context(playwright, browser, context)
    if args.command == "run":
        task = config.get_task(args.task)
        if task.profile != args.profile:
            raise ValueError(
                f"Task '{args.task}' is configured for profile '{task.profile}'"
            )
        result = run_task(profile, task, log_level=args.log_level)
        print(f"run completed ok={result.ok}")
        print(f"run stub for profile={args.profile} task={args.task}")
        return 0
    if args.command == "debug-network":
        print(f"debug-network stub for profile={args.profile}")
        return 0
    if args.command == "smoke":
        playwright = browser = context = None
        try:
            playwright, browser, context = create_context(profile)
            page = context.new_page()
            page.goto(profile.start_url)
            time.sleep(3)
            return 0
        finally:
            if context and browser and playwright:
                close_context(playwright, browser, context)
    if args.command == "print-config":
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
