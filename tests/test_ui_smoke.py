"""Pre-flight smoke test: boot the app through onboarding + main screens
with mocked Gemini/SMTP to catch NameErrors before they hit production."""

import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))))


class TestAppSmoke(unittest.TestCase):
    """Minimal end-to-end sanity checks using streamlit.testing.v1.AppTest."""

    def _mock_gemini(self):
        chat = MagicMock()
        chat.send_message.return_value.text = (
            '[{"title":"Midterm","date":"2026-11-01","confidence":"high"}]'
        )
        chat.client.chats.create.return_value = chat
        chat.config = MagicMock()
        chat.config.system_instruction = "test"
        return chat

    @patch('app.get_gemini_client')
    def test_onboarding_submits_without_exception(self, mock_get_client):
        from streamlit.testing.v1 import AppTest
        mock_chat = self._mock_gemini()
        mock_get_client.return_value.chats.create.return_value = mock_chat
        at = AppTest("app.py", default_timeout=10)
        at.run()
        at.text_input[0].set_value("Test Student")
        at.text_input[1].set_value("test@university.edu")
        at.button[0].click()
        at.run()
        self.assertTrue(at.session_state.get("onboarded", False))

    @patch('app.get_gemini_client')
    def test_post_onboarding_chat_sends_no_exception(self, mock_get_client):
        from streamlit.testing.v1 import AppTest
        mock_chat = self._mock_gemini()
        mock_get_client.return_value.chats.create.return_value = mock_chat
        at = AppTest("app.py", default_timeout=10)
        at.run()
        at.session_state["onboarded"] = True
        at.session_state["name"] = "Test Student"
        at.session_state["email"] = "test@university.edu"
        at.session_state["chat"] = mock_chat
        at.session_state["messages"] = [
            {"role": "assistant", "kind": "text", "content": "Welcome Test Student!"}
        ]
        at.session_state["deadlines"] = []
        at.run()
        at.chat_input[0].set_value("When is my midterm?")
        at.run()
        self.assertEqual(len(at.session_state["messages"]), 3)
        self.assertEqual(at.session_state["messages"][1]["role"], "user")
        self.assertEqual(at.session_state["messages"][2]["role"], "assistant")


class TestUIHelpers(unittest.TestCase):
    """Verify ui.py helpers produce clean, parseable HTML."""

    def test_no_blank_lines_or_leading_spaces_in_helpers(self):
        """No ui.py helper should emit blank lines or 4+ space indents."""
        import ui

        helpers = [
            name for name in dir(ui)
            if not name.startswith("_") and callable(getattr(ui, name))
        ]

        for helper_name in helpers:
            fn = getattr(ui, helper_name)
            try:
                # Call with minimal args where needed
                if helper_name == "hero_html":
                    result = fn("Test", "Tagline")
                elif helper_name == "chip_html":
                    result = fn("Label", "upcoming")
                elif helper_name == "glass_card_html":
                    result = fn("<p>test</p>")
                elif helper_name in ("empty_chat_html", "empty_deadlines_html", "empty_workload_html"):
                    result = fn()
                elif helper_name == "countdown_cards_html":
                    result = fn([])
                elif helper_name in ("quick_action_pills_html", "urgency_chips_html", "step_strip_html", "feature_cards_html", "divider_html", "section_title_html"):
                    result = fn()
                elif helper_name == "onboarding_card_html":
                    result = fn()
                else:
                    continue

                lines = result.splitlines()
                for i, line in enumerate(lines):
                    stripped = line.rstrip()
                    if stripped == "":
                        self.fail(
                            f"{helper_name}() returned a blank line at index {i}: {result!r}"
                        )
                    if line.startswith("    "):
                        self.fail(
                            f"{helper_name}() has a line starting with 4+ spaces "
                            f"at index {i}: {line!r}"
                        )
            except TypeError:
                # Skip helpers that need args we can't provide
                pass


class TestMarkdownSafety(unittest.TestCase):
    """Every st.markdown() with HTML tags must use unsafe_allow_html=True."""

    def test_markdown_with_html_has_unsafe_allow_html(self):
        import ast
        with open("app.py", encoding="utf-8") as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "markdown":
                # Find if unsafe_allow_html=True is passed
                has_unsafe = any(
                    kw.arg == "unsafe_allow_html" and isinstance(kw.value, ast.Constant) and kw.value.value is True
                    for kw in node.keywords
                )
                # Check if the first arg contains HTML tags
                if node.args:
                    arg = node.args[0]
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        if "<div" in arg.value or "<span" in arg.value or "<section" in arg.value:
                            self.assertTrue(
                                has_unsafe,
                                f"st.markdown() at line {node.lineno} contains HTML but lacks unsafe_allow_html=True"
                            )


if __name__ == "__main__":
    unittest.main()
