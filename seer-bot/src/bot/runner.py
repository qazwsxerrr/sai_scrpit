"""Task runner with logging, screenshots, and tracing."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from bot.browser import close_context, create_context
from bot.config import ProfileConfig, TaskConfig
from bot.utils.logging import log_event, setup_logging
from bot.utils.paths import logs_dir, traces_dir


@dataclass
class RunResult:
    ok: bool
    screenshot_path: Path | None = None
    trace_path: Path | None = None


def _should_trace(task: TaskConfig) -> str:
    trace_setting = task.trace or task.params.get("trace") or "never"
    return trace_setting


def run_task(profile: ProfileConfig, task: TaskConfig, log_level: str = "INFO") -> RunResult:
    log_path = logs_dir() / "run.jsonl"
    logger = setup_logging(log_path, level=log_level)

    trace_setting = _should_trace(task)
    playwright = browser = context = None
    page = None
    trace_path: Path | None = None
    screenshot_path: Path | None = None

    start = time.monotonic()
    log_event(logger, "task_start", profile=task.profile, task=task.name, step="start")

    try:
        playwright, browser, context = create_context(profile)
        if trace_setting in {"always", "on_fail"}:
            context.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = context.new_page()
        page.goto(profile.start_url)

        if task.params.get("force_fail"):
            raise RuntimeError("Forced failure for testing")

        elapsed_ms = int((time.monotonic() - start) * 1000)
        log_event(
            logger,
            "task_success",
            profile=task.profile,
            task=task.name,
            step="done",
            elapsed_ms=elapsed_ms,
        )
        if trace_setting == "always":
            trace_path = traces_dir() / f"{task.name}.zip"
            context.tracing.stop(path=str(trace_path))
        return RunResult(ok=True, trace_path=trace_path)
    except Exception as exc:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        log_event(
            logger,
            "task_failure",
            profile=task.profile,
            task=task.name,
            step="error",
            elapsed_ms=elapsed_ms,
        )
        if context is not None and page is not None:
            screenshot_path = logs_dir() / f"{task.name}_fail.png"
            page.screenshot(path=str(screenshot_path))
            if trace_setting in {"always", "on_fail"}:
                trace_path = traces_dir() / f"{task.name}.zip"
                context.tracing.stop(path=str(trace_path))
        raise RuntimeError(str(exc)) from exc
    finally:
        if context and browser and playwright:
            close_context(playwright, browser, context)
