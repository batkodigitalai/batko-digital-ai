from unittest.mock import MagicMock

import pytest

from src.openlane.browser import BrowserMode, BrowserRuntime, SessionManager


def make_runtime() -> BrowserRuntime:
    return BrowserRuntime(
        mode=BrowserMode.LOCAL,
        playwright=MagicMock(name="playwright"),
        browser=MagicMock(name="browser"),
        context=MagicMock(name="context"),
        page=MagicMock(name="page"),
        owns_browser=True,
        owns_context=True,
    )


def test_session_manager_creates_and_ends_session() -> None:
    runtime = make_runtime()
    browser_manager = MagicMock(name="browser_manager")
    browser_manager.start.return_value = runtime
    session = SessionManager(browser_manager)

    assert session.create_session() is runtime
    assert session.get_active_page() is runtime.page
    assert session.get_browser_context() is runtime.context

    session.end_session()

    browser_manager.stop.assert_called_once_with(runtime)


def test_session_manager_requires_active_session() -> None:
    session = SessionManager(MagicMock(name="browser_manager"))

    with pytest.raises(RuntimeError):
        session.get_active_page()

    with pytest.raises(RuntimeError):
        session.get_browser_context()

