"""Unit tests for the Gemini 503 retry logic in ask_gemini() and extract_deadlines().

These tests import the real ``app`` module (which imports the real ``streamlit``),
then replace the streamlit module object on ``app.st`` with a controlled mock so
that no network or UI calls are made.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch


# Ensure the project root is on sys.path so ``import app`` works.
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))))


class _SessionState(dict):
    """Thin wrapper so plain attr access works (like Streamlit session state)."""
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'") from None
    def __setattr__(self, key, value):
        self[key] = value


def _make_fake_st(session_state: dict) -> MagicMock:
    """Return a mock streamlit module pre-seeded with *session_state*."""
    mock_st = MagicMock(spec=["session_state", "secrets", "spinner", "error",
                              "info", "success", "warning", "title", "caption",
                              "write", "image", "button", "rerun", "stop",
                              "chat_message", "form", "text_input",
                              "form_submit_button", "expander", "markdown",
                              "columns", "tab", "tabs", "dataframe",
                              "download_button", "metric"])
    # Use a real dict (wrapped for attr access) so app.st.session_state.chat works.
    ss = _SessionState(session_state)
    mock_st.session_state = ss
    mock_st.secrets = {
        "GEMINI_API_KEY": "fake_key",
        "GMAIL_ADDRESS": "test@gmail.com",
        "GMAIL_APP_PASSWORD": "abcdefghijklmnop",
    }
    for name in ("spinner", "error", "info", "success", "warning", "title",
                 "caption", "write", "image", "button", "rerun", "stop",
                 "chat_message", "form", "text_input", "form_submit_button",
                 "expander", "markdown", "columns", "tab", "tabs",
                 "dataframe", "download_button", "metric"):
        setattr(mock_st, name, MagicMock())
    return mock_st


class TestAskGeminiRetry(unittest.TestCase):
    """Tests for the 503/UNAVAILABLE retry behaviour inside ask_gemini()."""

    def _patch_app_st(self, chat) -> MagicMock:
        """Install a fake streamlit mock on app.st and return it."""
        import app
        session = {
            "chat": chat,
            "deadlines": [],
            "messages": [],
            "sending": False,
            "onboarded": False,
            "name": "",
            "email": "",
        }
        fake_st = _make_fake_st(session)
        app.st = fake_st  # type: ignore[misc]
        return fake_st

    def test_retry_then_success_returns_text(self):
        """First two calls raise 503, third succeeds — returns the success text."""
        import app

        chat = MagicMock()
        chat.send_message.side_effect = [
            Exception("503 UNAVAILABLE high demand"),
            Exception("503 UNAVAILABLE, please try again later"),
            MagicMock(text="Success after retries!"),
        ]

        self._patch_app_st(chat)
        with patch.object(app.st, 'spinner', MagicMock()):
            result = app.ask_gemini([MagicMock()])

        self.assertEqual(result, "Success after retries!")
        self.assertEqual(chat.send_message.call_count, 3)

    def test_permanent_error_not_retried(self):
        """401/403/400 errors are NOT retried — immediate friendly message."""
        import app

        chat = MagicMock()
        chat.send_message.side_effect = [
            Exception("401 Unauthorized: Invalid API key"),
        ]

        self._patch_app_st(chat)
        with patch.object(app.st, 'spinner', MagicMock()):
            result = app.ask_gemini([MagicMock()])

        # Should NOT get the retry message; should get the generic error
        self.assertNotEqual(
            result,
            "Google's AI is very busy right now. Please wait a few seconds and send again."
        )
        self.assertIn("401", result)
        self.assertEqual(chat.send_message.call_count, 1)  # no retries

    def test_all_retries_fail_gives_friendly_message(self):
        """All three retries raise 503 — returns the friendly message."""
        import app

        chat = MagicMock()
        chat.send_message.side_effect = [
            Exception("503 UNAVAILABLE"),
            Exception("RESOURCE_EXHAUSTED"),
            Exception("503 UNAVAILABLE"),
            Exception("503 UNAVAILABLE"),  # the 4th call (beyond MAX_RETRIES)
        ]

        self._patch_app_st(chat)
        with patch.object(app.st, 'spinner', MagicMock()):
            result = app.ask_gemini([MagicMock()])

        self.assertEqual(
            result,
            "Google's AI is very busy right now. Please wait a few seconds and send again."
        )
        # 1 initial + 3 retries = 4 calls
        self.assertEqual(chat.send_message.call_count, 4)


class TestExtractDeadlinesPreservesTable(unittest.TestCase):
    """Test that extract_deadlines() failure never wipes the existing deadlines table."""

    def test_failure_does_not_wipe_deadlines(self):
        """When extraction raises, the existing session deadlines are untouched."""
        import app

        chat = MagicMock()
        chat.send_message.side_effect = Exception("503 UNAVAILABLE")

        existing_deadlines = [
            {"id": "a", "title": "Old Deadline", "date": "2024-12-01"}
        ]

        session = {
            "chat": chat,
            "deadlines": existing_deadlines,
            "messages": [],
            "sending": False,
            "onboarded": False,
            "name": "",
            "email": "",
        }
        fake_st = _make_fake_st(session)
        app.st = fake_st  # type: ignore[misc]

        with patch.object(app.st, 'spinner', MagicMock()), \
             patch.object(app.st, 'error'):
            result = app.extract_deadlines()

        # Returns empty list, does NOT modify session_state.deadlines
        self.assertEqual(result, [])
        self.assertEqual(app.st.session_state["deadlines"], existing_deadlines)


if __name__ == '__main__':
    unittest.main()
