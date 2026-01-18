"""Directory helpers for state, logs, and traces."""

from __future__ import annotations

from datetime import date
from pathlib import Path

BASE_DIR = Path.cwd()


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def state_dir(profile: str) -> Path:
    return _ensure_dir(BASE_DIR / "state" / profile)


def logs_dir(day: date | None = None) -> Path:
    day = day or date.today()
    return _ensure_dir(BASE_DIR / "logs" / day.isoformat())


def traces_dir(day: date | None = None) -> Path:
    day = day or date.today()
    return _ensure_dir(BASE_DIR / "traces" / day.isoformat())


def ensure_profile_dirs(profile: str) -> None:
    state_dir(profile)
    logs_dir()
    traces_dir()
