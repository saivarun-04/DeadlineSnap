"""SMTP Diagnostic Script for DeadlineSnap

Run this script to verify your Gmail credentials and network connectivity:
    python tools/test_smtp.py

It tests port 465 (SSL) and port 587 (STARTTLS) separately, then sends
a short test email to the address stored in .streamlit/secrets.toml.

Important: The app password must be entered as a single 16-character string
with no spaces. Google displays them in groups of 4, but they must be sent
as one continuous string.
"""

import smtplib
import ssl
import sys
import os

# ---------------------------------------------------------------------------
# Read secrets
# ---------------------------------------------------------------------------
SECRETS_PATH = os.path.join(os.path.dirname(__file__), '..', '.streamlit', 'secrets.toml')

def read_secrets():
    """Read GMAIL_ADDRESS and GMAIL_APP_PASSWORD from secrets.toml"""
    try:
        import tomllib
    except ImportError:
        # Python < 3.11 fallback
        import toml as tomllib

    with open(SECRETS_PATH, 'rb') as f:
        data = tomllib.load(f)

    address = data.get('GMAIL_ADDRESS', '').strip()
    # Strip ALL whitespace from app password (Google displays "abcd efgh ijkl mnop")
    password = data.get('GMAIL_APP_PASSWORD', '').replace(' ', '').replace('\t', '')

    if not address or address.startswith('PASTE_'):
        print("ERROR: GMAIL_ADDRESS is missing or still has the PASTE_ placeholder.")
        print("Edit .streamlit/secrets.toml with your real values.")
        sys.exit(1)
    if not password or password.startswith('PASTE_'):
        print("ERROR: GMAIL_APP_PASSWORD is missing or still has the PASTE_ placeholder.")
        print("Edit .streamlit/secrets.toml with your real 16-char app password.")
        sys.exit(1)

    return address, password


# ---------------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------------
CONNECT_TIMEOUT = 20
SSL_PORT = 465
STARTTLS_PORT = 587
SMTP_HOST = 'smtp.gmail.com'


def try_ssl(address: str, password: str) -> tuple[bool, str]:
    """Test connection on port 465 (SMTP_SSL)."""
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SSL_PORT, context=context, timeout=CONNECT_TIMEOUT) as server:
            server.login(address, password)
            return True, "OK — login successful on port 465 (SSL)"
    except smtplib.SMTPAuthenticationError as e:
        return False, f"AUTH FAIL on 465: {e}"
    except (ConnectionError, TimeoutError, OSError, ssl.SSLError) as e:
        return False, f"CONN FAIL on 465 ({type(e).__name__}): {e}"


def try_starttls(address: str, password: str) -> tuple[bool, str]:
    """Test connection on port 587 (STARTTLS)."""
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, STARTTLS_PORT, timeout=CONNECT_TIMEOUT) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(address, password)
            return True, "OK — login successful on port 587 (STARTTLS)"
    except smtplib.SMTPAuthenticationError as e:
        return False, f"AUTH FAIL on 587: {e}"
    except (ConnectionError, TimeoutError, OSError, ssl.SSLError) as e:
        return False, f"CONN FAIL on 587 ({type(e).__name__}): {e}"


# ---------------------------------------------------------------------------
# Send test email
# ---------------------------------------------------------------------------
def send_test_email(address: str, password: str) -> tuple[bool, str]:
    """Send a test email to self using the best working port."""
    # Try 465 first, fall back to 587
    for port, use_ssl in [(465, True), (587, False)]:
        try:
            context = ssl.create_default_context()
            if use_ssl:
                with smtplib.SMTP_SSL(SMTP_HOST, port, context=context, timeout=CONNECT_TIMEOUT) as s:
                    s.login(address, password)
                    msg = (
                        "From: " + address + "\r\n"
                        "To: " + address + "\r\n"
                        "Subject: DeadlineSnap SMTP Test\r\n\r\n"
                        "If you received this email, SMTP authentication is working correctly!\r\n"
                        "This was sent automatically by DeadlineSnap's SMTP diagnostic tool."
                    )
                    s.sendmail(address, [address], msg)
                    return True, f"Test email sent successfully via port {port}"
            else:
                with smtplib.SMTP(SMTP_HOST, port, timeout=CONNECT_TIMEOUT) as s:
                    s.ehlo()
                    s.starttls(context=context)
                    s.ehlo()
                    s.login(address, password)
                    msg = (
                        "From: " + address + "\r\n"
                        "To: " + address + "\r\n"
                        "Subject: DeadlineSnap SMTP Test\r\n\r\n"
                        "If you received this email, SMTP authentication is working correctly!\r\n"
                        "This was sent automatically by DeadlineSnap's SMTP diagnostic tool."
                    )
                    s.sendmail(address, [address], msg)
                    return True, f"Test email sent successfully via port {port}"
        except Exception as e:
            continue
    return False, "Failed to send test email via any method."


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("DeadlineSnap SMTP Diagnostic Tool")
    print("=" * 60)
    print()

    address, password = read_secrets()
    print(f"Target address : {address}")
    print(f"Password length: {len(password)} chars")
    print()

    print("--- Step 1: Port 465 (SMTP_SSL) ---")
    ok465, msg465 = try_ssl(address, password)
    print(f"  {'PASS' if ok465 else 'FAIL'} {msg465}")

    print()
    print("--- Step 2: Port 587 (STARTTLS) ---")
    ok587, msg587 = try_starttls(address, password)
    print(f"  {'PASS' if ok587 else 'FAIL'} {msg587}")

    print()
    print("--- Step 3: Send test email ---")
    ok_send, msg_send = send_test_email(address, password)
    print(f"  {'PASS' if ok_send else 'FAIL'} {msg_send}")

    print()
    print("--- Interpretation ---")
    if ok465:
        print("Port 465 SSL works — your network allows SMTP SSL connections.")
    if ok587:
        print("Port 587 STARTTLS works — your network allows SMTP STARTTLS connections.")
    if not ok465 and not ok587:
        print("Both ports failed (connection issue). Your network (college Wi-Fi, firewall,")
        print("or antivirus) may be blocking SMTP entirely. Try a mobile hotspot.")
    if (ok465 or ok587) and not ok_send:
        print("Connection worked but sending failed. Check spam folder or Gmail quotas.")

    if not ok465 and ok587:
        print()
        print("NOTE: Port 465 failed but 587 works. The app will automatically fall back")
        print("to port 587 on your behalf, so this is fine.")

    if ok465 and not ok587:
        print()
        print("NOTE: Port 587 failed but 465 works. This is unusual but acceptable.")

    print()
    print("=" * 60)
    if ok_send:
        print("SUCCESS! Your credentials are valid and email delivery works.")
    else:
        print("PROBLEM: Email delivery failed. See messages above for details.")
    print("=" * 60)


if __name__ == '__main__':
    main()