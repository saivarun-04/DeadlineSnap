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


if __name__ == "__main__":
    unittest.main()
