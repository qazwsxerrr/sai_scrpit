"""Browser and context helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

from playwright.sync_api import Browser, BrowserContext, Playwright, sync_playwright

from bot.config import ProfileConfig


def create_browser(profile: ProfileConfig) -> tuple[Playwright, Browser]:
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        headless=profile.headless,
        slow_mo=profile.slow_mo_ms,
    )
    return playwright, browser


def create_context(
    profile: ProfileConfig, storage_state_path: str | Path | None = None
) -> Tuple[Playwright, Browser, BrowserContext]:
    playwright, browser = create_browser(profile)
    context = browser.new_context(
        viewport=profile.viewport,
        user_agent=profile.user_agent,
        timezone_id=profile.timezone,
        storage_state=str(storage_state_path) if storage_state_path else None,
    )
    return playwright, browser, context


def close_context(playwright: Playwright, browser: Browser, context: BrowserContext) -> None:
    context.close()
    browser.close()
    playwright.stop()
