"""Configuration loading and validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, ValidationError


class ProfileConfig(BaseModel):
    start_url: str
    headless: bool = True
    slow_mo_ms: int = 0
    timezone: str = "UTC"
    viewport: dict[str, int] = Field(default_factory=lambda: {"width": 1280, "height": 720})
    user_agent: str | None = None


class TaskConfig(BaseModel):
    name: str
    profile: str
    schedule: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)


class BotConfig(BaseModel):
    profiles: dict[str, ProfileConfig]
    tasks: list[TaskConfig] = Field(default_factory=list)

    def get_profile(self, name: str) -> ProfileConfig:
        try:
            return self.profiles[name]
        except KeyError as exc:
            raise KeyError(f"Profile '{name}' not found in config") from exc

    def get_task(self, name: str) -> TaskConfig:
        for task in self.tasks:
            if task.name == name:
                return task
        raise KeyError(f"Task '{name}' not found in config")


SENSITIVE_KEYS = ("token", "cookie", "secret", "password")


def _redact_value(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, val in value.items():
            if any(token in key.lower() for token in SENSITIVE_KEYS):
                redacted[key] = "***"
            else:
                redacted[key] = _redact_value(val)
        return redacted
    if isinstance(value, list):
        return [_redact_value(item) for item in value]
    return value


def redact_config(data: dict[str, Any]) -> dict[str, Any]:
    return _redact_value(data)


def load_config(path: str | Path) -> BotConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Config root must be a mapping")

    try:
        return BotConfig.model_validate(raw)
    except ValidationError as exc:
        raise ValueError(f"Invalid config: {exc}") from exc
