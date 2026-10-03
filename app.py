"""DeadlineSnap - AI Vision Chatbot for Deadline Tracking"""

import datetime
import json
import smtplib
import ssl
import uuid
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, Optional, List, Tuple, Callable

import streamlit as st
from google import genai
from google.genai import types

import prompts
import core
import ui

# Constants
MODEL_NAME = "gemini-3.5-flash"
MODEL_FALLBACKS = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]
PAGE_TITLE = "DeadlineSnap"
PAGE_ICON = "📅"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT_SSL = 465
SMTP_PORT_STARTTLS = 587
SMTP_TIMEOUT = 20


# Initialize page config
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")


# Cache Gemini client to avoid "client has been closed" bug
@st.cache_resource
def get_gemini_client() -> genai.Client:
    """Get cached Gemini client"""
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


# Secret validation
def validate_secrets() -> bool:
    """Check if all required secrets are present and not placeholders"""
    required_secrets = ["GEMINI_API_KEY", "GMAIL_ADDRESS", "GMAIL_APP_PASSWORD"]
    missing = []
    for key in required_secrets:
        if key not in st.secrets:
            missing.append(key)
        elif str(st.secrets[key]).strip().startswith("PASTE_"):
            missing.append(key)
    if missing:
        st.error(f"Missing or placeholder secrets: {', '.join(missing)}")
        st.error("Please add real values to your .streamlit/secrets.toml file")
        st.stop()
    return True


# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if "onboarded" not in st.session_state:
        st.session_state.onboarded = False
    if "name" not in st.session_state:
        st.session_state.name = ""
    if "email" not in st.session_state:
        st.session_state.email = ""
    if "chat" not in st.session_state:
        st.session_state.chat = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "deadlines" not in st.session_state:
        st.session_state.deadlines = []
    if "sending" not in st.session_state:
        st.session_state.sending = False


# Onboarding form
def render_onboarding():
    """Render the onboarding form"""
    with st.form("onboarding"):
        name = st.text_input("Your Name", placeholder="Enter your full name")
        email = st.text_input("Your Email", placeholder="student@university.edu")
        submitted = st.form_submit_button("Get Started")

        if submitted:
            if not name or not email:
                st.warning("Please fill in both fields")
                return
            # Basic email validation
            if "@" not in email or "." not in email.split("@")[1]:
                st.warning("Please enter a valid email address")
                return

            # Initialize chat
            client = get_gemini_client()
            system_prompt = prompts.build_system_prompt(datetime.date.today())
            config = types.GenerateContentConfig(system_instruction=system_prompt)
            chat = client.chats.create(model=MODEL_NAME, config=config)

            # Store in session state
            st.session_state.onboarded = True
            st.session_state.name = name
            st.session_state.email = email
            st.session_state.chat = chat
            st.session_state.messages = [
                {"role": "assistant", "kind": "text", "content": prompts.WELCOME_MESSAGE_TEMPLATE.format(name=name)}
            ]
            st.session_state.deadlines = []
            st.rerun()


# Chat UI helpers
def render_message(message: Dict[str, Any]):
    """Render a single message"""
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.write(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"], caption="Uploaded image")
            if message.get("text"):
                st.write(message["text"])


def add_message(role: str, kind: str, content: Any):
    """Add a message to the chat"""
    st.session_state.messages.append({"role": role, "kind": kind, "content": content})


def _retry_then_fallback(func: Callable, *args: Any, **kwargs: Any) -> Tuple[bool, Any]:
    """Wrap a Gemini call with retry + model fallback.

    First calls *func* with exponential-backoff jitter (core.call_with_retry).
    If that fails, iterates MODEL_FALLBACKS creating a new chat on each and
    replaying the existing conversation history.
    """
    success, result = core.call_with_retry(func, *args, **kwargs)
    if success:
        return True, result

    # All retries exhausted — try fallback models one by one
    for fallback_model in MODEL_FALLBACKS:
        try:
            st.toast(f"High demand, switching to {fallback_model}...", duration=2)
            # Build a fresh chat with the fallback model
            fallback_chat = st.session_state.chat.client.chats.create(
                model=fallback_model,
                config=types.GenerateContentConfig(
                    system_instruction=st.session_state.chat.config.system_instruction
                )
            )
            st.session_state.chat = fallback_chat
            # Replay existing messages (except the last one we're about to retry)
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    fallback_chat.send_message(msg["content"])
            # Now send the new parts
            resp = fallback_chat.send_message(args[0] if args else "")
            return True, resp.text
        except Exception:
            continue

    return False, None


# Ask Gemini
def ask_gemini(parts: List[types.Part]) -> str:
    """Ask Gemini with retry and model fallback."""
    success, result = _retry_then_fallback(st.session_state.chat.send_message, parts)
    if success:
        return result
    # All models failed
    models_str = f"{MODEL_NAME}, " + ", ".join(MODEL_FALLBACKS)
    st.error(
        f"Google's AI is very busy right now. I tried {models_str}. "
        "Please wait a few seconds and press Send again."
    )
    return "I'm sorry, I couldn't get a response right now. Please try again in a moment."


# Process uploaded image
def process_image(uploaded_file) -> Optional[types.Part]:
    """Process uploaded image into Gemini Part"""
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        return types.Part.from_bytes(
            data=bytes_data,
            mime_type=uploaded_file.type
        )
    return None


# Extract deadlines from conversation
def extract_deadlines() -> List[Dict[str, Any]]:
    """Extract deadlines from conversation using hidden prompt.

    Uses call_with_retry so transient 503/429 errors never wipe the
    deadlines table — on failure we return an empty list and keep what's
    already in session state.
    """
    success, result = core.call_with_retry(
        st.session_state.chat.send_message,
        prompts.EXTRACTION_PROMPT,
    )
    if not success:
        st.warning(f"Could not extract deadlines right now ({result}). Your saved deadlines are untouched.")
        return []
    raw = result.text
    parsed = core.parse_json_safely(raw)
    return parsed


# Send email
def send_email(to_address: str, subject: str, body: str, ics_bytes: bytes) -> Tuple[bool, str]:
    """Send email with Gmail SMTP using SSL (465) or STARTTLS (587).

    The app password is stripped of all whitespace because Google displays
    them in groups of 4 characters, but SMTP requires a continuous string.
    """
    gmail_address = st.secrets["GMAIL_ADDRESS"].strip()
    # Strip ALL internal whitespace from the app password
    gmail_password = st.secrets["GMAIL_APP_PASSWORD"].replace(' ', '').replace('\t', '')

    msg = MIMEMultipart()
    msg['From'] = gmail_address
    msg['To'] = to_address
    msg['Subject'] = subject

    # Attach text body
    msg.attach(MIMEText(body, 'plain'))

    # Attach .ics file
    ics_part = MIMEBase('text', 'calendar')
    ics_part.set_payload(ics_bytes)
    ics_part.add_header('Content-Disposition', 'attachment', filename='deadlines.ics')
    msg.attach(ics_part)

    context = ssl.create_default_context()

    # Try SSL first (port 465)
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT_SSL, context=context, timeout=SMTP_TIMEOUT) as server:
            server.login(gmail_address, gmail_password)
            server.send_message(msg)
        return True, f"Email sent successfully via port {SMTP_PORT_SSL}"
    except smtplib.SMTPAuthenticationError:
        return False, "Gmail rejected the login. Use a 16-character App Password (myaccount.google.com/apppasswords), not your normal password, and make sure 2-Step Verification is on."
    except (smtplib.SMTPServerDisconnected, ConnectionError, TimeoutError, ssl.SSLError, OSError):
        pass  # Fall through to STARTTLS

    # Fallback to STARTTLS (port 587)
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT_STARTTLS, timeout=SMTP_TIMEOUT) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(gmail_address, gmail_password)
            server.send_message(msg)
        return True, f"Email sent successfully via port {SMTP_PORT_STARTTLS}"
    except smtplib.SMTPAuthenticationError:
        return False, "Gmail rejected the login. Use a 16-character App Password (myaccount.google.com/apppasswords), not your normal password, and make sure 2-Step Verification is on."
    except (smtplib.SMTPServerDisconnected, ConnectionError, TimeoutError, ssl.SSLError, OSError):
        pass  # Both failed

    # Neither port worked
    return False, (
        "Couldn't reach Gmail on port 465 or 587. Your network may be blocking SMTP "
        "(college Wi-Fi, firewall or antivirus). Try a mobile hotspot, or use the download buttons. "
        "It should work once deployed."
    )


# Build digest
def build_digest(deadlines: List[Dict[str, Any]], today: datetime.date) -> str:
    """Build plain text digest"""
    if not deadlines:
        return "No deadlines found"

    lines = [f"Hello {st.session_state.name},", "", "Here are your upcoming deadlines:"]

    # Group by urgency
    overdue = []
    next_week = []
    later = []

    for d in deadlines:
        label, days = core.urgency_label(d, today)
        if label == "🔴":
            overdue.append(d)
        elif label == "🟠":
            next_week.append(d)
        else:
            later.append(d)

    if overdue:
        lines.append("\n🔴 Overdue:")
        for d in overdue:
            lines.append(f"  • {d['date']} - {d['title']}")

    if next_week:
        lines.append("\n🟠 Next 7 days:")
        for d in next_week:
            lines.append(f"  • {d['date']} - {d['title']}")

    if later:
        lines.append("\n🟡 Later:")
        for d in later:
            lines.append(f"  • {d['date']} - {d['title']}")

    lines.append(f"\nTotal: {len(deadlines)} deadlines")
    lines.append("\nBest of luck with your studies! – DeadlineSnap")

    return "\n".join(lines)


# Main app
def main():
    """Main app function"""
    ui.inject_css()
    validate_secrets()
    init_session_state()

    # Hero banner (shown after onboarding)
    if st.session_state.get("onboarded"):
        ui.render_hero()

    # Chat input (outside tabs to avoid duplicate IDs)
    user_input = st.chat_input("Ask about deadlines or upload an image", accept_file=True, file_type=["jpg", "jpeg", "png"], key="chat_input")

    # Tabs
    tabs = st.tabs(["💬 Chat", "📋 Deadlines", "📊 Workload"])

    with tabs[0]:  # Chat tab
        _render_chat_tab(user_input)

    with tabs[1]:  # Deadlines tab
        _render_deadlines_tab()

    with tabs[2]:  # Workload tab
        _render_workload_tab()

    # Sidebar (always shown)
    _render_sidebar()


def _render_chat_tab(user_input):
    """Render the chat tab with quick actions and message history."""
    # Quick action chips
    if st.session_state.get("onboarded") and len(st.session_state.messages) > 1:
        ui.render_quick_actions()

    # Welcome message (only show once)
    if len(st.session_state.messages) == 1:
        render_message(st.session_state.messages[0])

    # Display chat history
    for msg in st.session_state.messages[1:]:
        render_message(msg)

    if user_input:
        # Check what type user_input is (text or uploaded file)
        parts = []

        if hasattr(user_input, 'text') and user_input.text:
            # Text input
            parts.append(types.Part.from_text(text=user_input.text))
            add_message("user", "text", user_input.text)
            render_message({"role": "user", "kind": "text", "content": user_input.text})
        elif hasattr(user_input, 'type'):
            # Image input
            bytes_data = user_input.getvalue()
            photo_part = types.Part.from_bytes(data=bytes_data, mime_type=user_input.type)
            parts.append(photo_part)
            parts.append(types.Part.from_text(text="List every deadline and date you can find in this image."))
            add_message("user", "image", bytes_data)
            render_message({"role": "user", "kind": "image", "content": bytes_data})
        else:
            # Fallback: treat as text
            parts.append(types.Part.from_text(text=str(user_input)))
            add_message("user", "text", str(user_input))
            render_message({"role": "user", "kind": "text", "content": str(user_input)})

        # Get Gemini response
        if parts:
            response = ask_gemini(parts)
            add_message("assistant", "text", response)
            render_message({"role": "assistant", "kind": "text", "content": response})

            # Extract deadlines from the conversation
            extracted = extract_deadlines()
            if extracted:
                st.session_state.deadlines = core.merge_deadlines(st.session_state.deadlines, extracted)

        # Retry button (shown after any exchange)
        if len(st.session_state.messages) > 2:
            if st.button("Retry last message"):
                # Find last user message and resend without adding duplicate
                last_user_idx = None
                for i in range(len(st.session_state.messages) - 1, -1, -1):
                    if st.session_state.messages[i]["role"] == "user":
                        last_user_idx = i
                        break
                if last_user_idx is not None:
                    last_msg = st.session_state.messages[last_user_idx]
                    # Re-add as user message (it will be re-rendered)
                    add_message("user", last_msg["kind"], last_msg["content"])
                    # Clear the failed assistant message if present
                    if (last_user_idx + 1 < len(st.session_state.messages) and
                            st.session_state.messages[last_user_idx + 1]["role"] == "assistant"):
                        st.session_state.messages.pop(last_user_idx + 1)
                    st.rerun()

        st.rerun()


def _render_deadlines_tab():
    """Render the deadlines tab with metrics, table, and email buttons."""
    deadlines = st.session_state.get("deadlines", [])
    today = datetime.date.today()

    if not deadlines:
        st.info("No deadlines extracted yet. Upload a photo or type deadlines in the chat.")
        return

    # Sort deadlines
    deadlines.sort(key=lambda d: d.get('date', '9999-12-31'))

    # Count by urgency
    overdue_count = sum(1 for d in deadlines if core.urgency_label(d, today)[0] == "🔴")
    warning_count = sum(1 for d in deadlines if core.urgency_label(d, today)[0] == "🟠")
    caution_count = sum(1 for d in deadlines if core.urgency_label(d, today)[0] == "🟡")

    # Metric cards for 3 nearest deadlines
    st.markdown('<div class="editor-card">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if overdue_count > 0:
            nearest_overdue = min(deadlines, key=lambda d: (d.get('date') or '9999')['0'])
            days = (datetime.datetime.strptime(nearest_overdue['date'], "%Y-%m-%d").date() - today).days
            ui.render_metric_card("Overdue", nearest_overdue.get('title', 'N/A'), abs(days), "overdue")
        else:
            ui.render_metric_card("Next Deadline", "No urgent items", "-", "safe")
    with col2:
        ui.render_metric_card("This Week", f"{warning_count} deadlines", f"{warning_count} days", "warning")
    with col3:
        ui.render_metric_card("This Month", f"{caution_count} deadlines", f"{caution_count} days", "caution")
    st.markdown('</div>', unsafe_allow_html=True)

    # Deadline table with edit capability
    st.markdown('<div class="editor-card">', unsafe_allow_html=True)
    st.subheader("Your Deadlines")
    st.caption("Edit the table below to fix any mistakes before emailing.")

    # Create DataFrame for editing
    import pandas as pd
    df = pd.DataFrame(deadlines)
    df_editable = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "date": st.column_config.DateColumn("Date", help="YYYY-MM-DD"),
            "time": st.column_config.TextColumn("Time", help="HH:MM"),
            "type": st.column_config.SelectboxColumn(
                "Type",
                options=["exam", "quiz", "assignment", "project", "lab", "event", "other"],
                help="Deadline type"
            ),
            "est_hours": st.column_config.NumberColumn("Est. Hours", help="Estimated study hours"),
            "weight": st.column_config.NumberColumn("Weight", help="Importance 1-5", min_value=1, max_value=5),
            "confidence": st.column_config.SelectboxColumn(
                "Confidence",
                options=["high", "medium", "low"],
                help="AI confidence in extraction"
            ),
        },
        key="deadline_editor"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Action buttons
    st.markdown('<div class="action-row">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        btn_disabled = st.session_state.get("sending", False)
        if st.button("Send Email Digest", type="primary", disabled=btn_disabled):
            st.session_state.sending = True
            st.rerun()
    with col2:
        if st.button("Download .ics"):
            ics_bytes = core.build_ics(deadlines)
            st.download_button(
                label="Download .ics",
                data=ics_bytes,
                file_name="deadlines.ics",
                mime="text/calendar"
            )
    with col3:
        csv_data = core.to_csv(deadlines)
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="deadlines.csv",
            mime="text/csv"
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Handle email sending
    if st.session_state.get("sending"):
        today = datetime.date.today()

        # Build digest
        digest = build_digest(deadlines, today)

        # Build .ics file
        ics_bytes = core.build_ics(deadlines)

        # Show preview
        with st.expander("Email Preview"):
            st.write(digest)

        # Send email
        success, message = send_email(
            st.session_state.email,
            f"Your {len(deadlines)} deadlines - DeadlineSnap",
            digest,
            ics_bytes
        )

        if success:
            st.success(message)
        else:
            st.error(message)
            st.info("You can still download the calendar file:")

        st.session_state.sending = False


def _render_workload_tab():
    """Render the workload tab with study plan and crunch warnings."""
    deadlines = st.session_state.get("deadlines", [])
    today = datetime.date.today()

    if not deadlines:
        st.info("No deadlines to analyze yet.")
        return

    # Daily max hours slider
    daily_max = st.slider("Daily study hours max", 1, 8, 3, key="daily_max_hours")

    # Build study plan
    sessions, unschedulable = core.build_study_plan(deadlines, daily_max, today)

    # Crunch day detection
    crunch_weeks = core.find_crunch_days(deadlines)

    if crunch_weeks:
        for week in crunch_weeks:
            ui.render_crunch_alert(
                f"Week of {week['sample_dates'][0] if week.get('sample_dates') else 'N/A'} "
                f"looks heavy: {week['deadlines']} deadlines, ~{week['hours']}h"
            )

    # Study plan table
    st.subheader("Study Plan")
    if sessions:
        import pandas as pd
        df_plan = pd.DataFrame(sessions)
        st.dataframe(df_plan, use_container_width=True)
    else:
        st.info("No study sessions scheduled. Try adjusting daily hours or check deadline dates.")

    if unschedulable:
        st.warning(f"⚠️ {len(unschedulable)} deadline(s) couldn't be scheduled - not enough time:")
        for item in unschedulable:
            st.caption(f"- {item.get('title', 'Unknown')} ({item.get('date', 'N/A')})")

    # Bar chart of planned hours per day
    if sessions:
        st.subheader("Planned Hours by Day")
        import pandas as pd
        df_hours = pd.DataFrame(sessions).groupby('date')['hours'].sum()
        st.bar_chart(df_hours)


def _render_sidebar():
    """Render the sidebar with user info and how-it-works."""
    with st.sidebar:
        if st.session_state.get("onboarded"):
            ui.render_user_chip(st.session_state.name, st.session_state.email)
            st.markdown("---")

        st.subheader("How it works")
        ui.render_stepper()
        st.markdown("")
        ui.render_tip_card()
        st.markdown("")

        if st.button("Start Over"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


if __name__ == "__main__":
    main()