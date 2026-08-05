"""Shared browser infrastructure models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class BrowserMode(StrEnum):
    """Supported browser startup modes."""

    LOCAL = "local"
    EXISTING_CHROME = "existing_chrome"
    PERSISTENT_PROFILE = "persistent_profile"


@dataclass(frozen=True)
class BrowserRuntime:
    """Runtime handles returned by BrowserManager.

    Handles are typed as Any because Playwright is intentionally isolated from
    business modules and mocked in unit tests.
    """

    mode: BrowserMode
    playwright: Any
    browser: Any
    context: Any
    page: Any
    owns_browser: bool
    owns_context: bool

