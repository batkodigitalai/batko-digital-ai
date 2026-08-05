"""Lazy Playwright provider.

Playwright is imported only when a real browser session is requested so unit
tests can exercise infrastructure without launching Chrome.
"""

from __future__ import annotations


def start_sync_playwright():
    """Start Playwright synchronously."""
    from playwright.sync_api import sync_playwright

    return sync_playwright().start()

