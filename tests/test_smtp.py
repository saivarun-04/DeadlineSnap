"""Unit tests for SMTP email functionality (with mocks)"""

import unittest
from unittest.mock import MagicMock, patch, call
import smtplib
import ssl
import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSendEmail(unittest.TestCase):
    """Test cases for the send_email function in app.py"""

    def setUp(self):
        """Set up test fixtures"""
        # Mock streamlit secrets
        self.test_secrets = {
            "GEMINI_API_KEY": "test_key",
            "GMAIL_ADDRESS": "test@gmail.com",
            "GMAIL_APP_PASSWORD": "abcd efgh ijkl mnop"  # With spaces (common Google format)
        }

    @patch('app.st')
    def test_password_whitespace_stripped(self, mock_st):
        """Test that spaces are stripped from app password before login"""
        import app

        # Set up mock secrets
        mock_st.secrets = self.test_secrets

        # Capture the call
        with patch('smtplib.SMTP_SSL') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
            mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

            # Call send_email
            result = app.send_email(
                to_address="recipient@gmail.com",
                subject="Test",
                body="Test body",
                ics_bytes=b"test ics content"
            )

            # Verify login was called with stripped password
            mock_server.login.assert_called_once()
            call_args = mock_server.login.call_args
            password_used = call_args[0][1]
            self.assertEqual(password_used, "abcdefghijklmnop")
            self.assertNotIn(' ', password_used)

    @patch('app.st')
    def test_fallback_to_starttls_on_ssl_failure(self, mock_st):
        """Test that we fall back to port 587 when 465 fails with connection error"""
        import app

        mock_st.secrets = self.test_secrets

        # Mock SMTP_SSL to raise connection error
        with patch('smtplib.SMTP_SSL', side_effect=smtplib.SMTPServerDisconnected("Connection reset")):
            with patch('smtplib.SMTP') as mock_smtp:
                mock_server = MagicMock()
                mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
                mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

                result = app.send_email(
                    to_address="recipient@gmail.com",
                    subject="Test",
                    body="Test body",
                    ics_bytes=b"test ics content"
                )

                # Should have fallen back to 587
                self.assertTrue(result[0])
                self.assertIn("587", result[1])
                # Verify STARTTLS methods were called
                mock_server.ehlo.assert_called()
                mock_server.starttls.assert_called_once()

    @patch('app.st')
    def test_authentication_error_returns_hint(self, mock_st):
        """Test that auth errors return the helpful hint without fallback"""
        import app

        mock_st.secrets = self.test_secrets

        # Mock SMTP_SSL to raise authentication error
        with patch('smtplib.SMTP_SSL', side_effect=smtplib.SMTPAuthenticationError(435, "Auth failed")):
            result = app.send_email(
                to_address="recipient@gmail.com",
                subject="Test",
                body="Test body",
                ics_bytes=b"test ics content"
            )

            # Should return auth error message, not try 587
            self.assertFalse(result[0])
            self.assertIn("App Password", result[1])
            self.assertNotIn("587", result[1])

    @patch('app.st')
    def test_both_ports_fail_returns_network_hint(self, mock_st):
        """Test when both ports fail, we get the network block message"""
        import app

        mock_st.secrets = self.test_secrets

        # Mock both SSL and SMTP to fail
        with patch('smtplib.SMTP_SSL', side_effect=ConnectionError("Network error")):
            with patch('smtplib.SMTP', side_effect=ConnectionError("Network error")):
                result = app.send_email(
                    to_address="recipient@gmail.com",
                    subject="Test",
                    body="Test body",
                    ics_bytes=b"test ics content"
                )

                # Should return network block message
                self.assertFalse(result[0])
                self.assertIn("college Wi-Fi", result[1])


class TestValidateSecrets(unittest.TestCase):
    """Test secret validation"""

    @patch('app.st')
    def test_paste_placeholder_detected(self, mock_st):
        """Test that PASTE_ placeholders are detected"""
        import app

        mock_st.secrets = {
            "GEMINI_API_KEY": "PASTE_GEMINI_KEY_HERE",
            "GMAIL_ADDRESS": "test@gmail.com",
            "GMAIL_APP_PASSWORD": "test_password"
        }

        # st.stop() raises SystemExit - verify it's called
        mock_st.stop.side_effect = SystemExit("test")
        with self.assertRaises(SystemExit):
            app.validate_secrets()

    @patch('app.st')
    def test_real_values_pass(self, mock_st):
        """Test that real values pass validation"""
        import app

        mock_st.secrets = {
            "GEMINI_API_KEY": "real_key",
            "GMAIL_ADDRESS": "test@gmail.com",
            "GMAIL_APP_PASSWORD": "abcd efgh ijkl mnop"
        }

        result = app.validate_secrets()
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()