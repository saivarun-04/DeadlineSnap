"""DeadlineSnap - AI Vision Chatbot for Deadline Tracking"""

import datetime
import smtplib
import ssl
import time
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, Optional, List, Tuple

import streamlit as st
from google import genai
from google.genai import types

import prompts
import core
from ui import inject_css, hero_html, step_strip_html, feature_cards_html, \
    empty_chat_html, empty_deadlines_html, \
    empty_workload_html, countdown_cards_html, urgency_chips_html, \
    quick_action_pills_html, divider_html, section_title_html
from html import escape as html_escape

# Constants
MODEL_NAME = "gemini-3.5-flash"
PAGE_TITLE = "DeadlineSnap"
PAGE_ICON = "📅"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT_SSL = 465
SMTP_PORT_STARTTLS = 587
SMTP_TIMEOUT = 20


# Initialize page config
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")
inject_css()


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
    """Render the onboarding form inside a glass card."""
    # Card header inside the form
    st.markdown(
        '<div style="text-align:center;margin-bottom:1.5rem;">'
        '<h2 style="margin:0 0 .25rem;font-size:1.3rem;font-weight:700;color:var(--ds-text);">'
        'Get started — it\'s free</h2>'
        '<p style="margin:0;font-size:.88rem;color:var(--ds-muted);">No credit card. No sign-up wall. Just your deadlines.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    with st.form("onboarding"):
        name = st.text_input("Your Name", placeholder="Enter your full name")
        st.caption('So we can greet you')
        email = st.text_input("Your Email", placeholder="student@university.edu")
        st.caption("We'll send your deadline digest here")
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


# Ask Gemini
def ask_gemini(parts: List[types.Part]) -> str:
    """Ask Gemini with parts and return response.

    On 503/UNAVAILABLE/429 errors, retries up to 3 times with exponential
    backoff (2s, 4s, 8s) using the SAME chat session. If all retries fail,
    returns a friendly message instead of raw JSON or raw exception text.
    Also falls back to gemini-2.5-flash on model-not-found errors.
    """
    RETRYABLE_KEYWORDS = ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "overloaded")
    MAX_RETRIES = 3
    BACKOFF_SECS = [2, 4, 8]

    try:
        with st.spinner("Reading your timetable..."):
            response = st.session_state.chat.send_message(parts)
            return response.text
    except Exception as e:
        err_str = str(e)
        is_retryable = any(kw in err_str for kw in RETRYABLE_KEYWORDS)
        if is_retryable:
            for attempt, wait in enumerate(BACKOFF_SECS):
                if attempt >= MAX_RETRIES:
                    break
                with st.spinner(f"Google's AI is busy — retrying ({attempt+1}/{MAX_RETRIES})..."):
                    time.sleep(wait)
                    try:
                        response = st.session_state.chat.send_message(parts)
                        return response.text
                    except Exception:
                        pass
            return "Google's AI is very busy right now. Please wait a few seconds and send again."

        # Try fallback model on model-not-found error
        if "model" in err_str.lower() or "not found" in err_str.lower():
            try:
                with st.spinner("Switching to gemini-2.5-flash..."):
                    fallback_chat = st.session_state.chat.client.chats.create(
                        model="gemini-2.5-flash",
                        config=types.GenerateContentConfig(
                            system_instruction=st.session_state.chat.config.system_instruction
                        )
                    )
                    response = fallback_chat.send_message(parts)
                    st.session_state.chat = fallback_chat
                    return response.text
            except Exception:
                pass
        return f"Sorry, I encountered an error: {err_str}. Please try again."


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

    On failure, logs an error but never wipes the existing deadlines table.
    """
    try:
        with st.spinner("Extracting deadlines..."):
            response = st.session_state.chat.send_message(prompts.EXTRACTION_PROMPT)
            raw = response.text
            parsed = core.parse_json_safely(raw)
            return parsed
    except Exception as e:
        st.error(f"Error extracting deadlines: {str(e)}")
        return []


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


# ─── Landing page (shown before onboarding) ───────────────────────────────────

def render_landing():
    """Render the landing / onboarding page."""
    # Hero
    st.markdown(hero_html(PAGE_TITLE, "Never miss a submission again."), unsafe_allow_html=True)
    st.markdown(step_strip_html(), unsafe_allow_html=True)
    st.markdown(divider_html(), unsafe_allow_html=True)

    # Onboarding form inside glass card
    render_onboarding()
    st.markdown(
        '<p style="text-align:center;font-size:.75rem;color:var(--ds-muted);margin-top:1rem;">'
        'Your photos and email are used only in this session and are never stored.</p>',
        unsafe_allow_html=True,
    )
    st.markdown(divider_html(), unsafe_allow_html=True)

    # Feature cards
    st.markdown(feature_cards_html(), unsafe_allow_html=True)

    # Who it's for
    st.markdown(
        '<p style="text-align:center;color:var(--ds-muted);font-size:.9rem;margin-top:1rem;">'
        'Built for students juggling many subjects, late-night study sessions, and chaotic timetables.</p>',
        unsafe_allow_html=True,
    )


# ─── Main app (shown after onboarding) ───────────────────────────────────────

def render_main():
    """Render the main app after onboarding — chat, deadlines, workload tabs."""
    name = st.session_state.name
    deadlines = st.session_state.deadlines
    n_dl = len(deadlines)

    # Compact header
    st.markdown(
        f'<p style="font-size:.95rem;color:var(--ds-muted);margin:0 0 .25rem;">'
        f'Welcome back, <strong style="color:var(--ds-text);">{html_escape(name)}</strong></p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p style="font-size:.8rem;color:var(--ds-muted);margin:0 0 1rem;">'
        f'{n_dl} deadline{"s" if n_dl != 1 else ""} tracked</p>',
        unsafe_allow_html=True,
    )

    # Tabs: Chat · Deadlines · Workload
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📅 Deadlines", "📊 Workload"])

    # ── Chat tab ──────────────────────────────────────────────────────────────
    with tab1:
        # Quick-action pills
        st.markdown(quick_action_pills_html(), unsafe_allow_html=True)

        # Welcome / empty state
        if len(st.session_state.messages) <= 1:
            st.markdown(
                empty_chat_html(
                    "Upload a photo of your timetable or syllabus, or type something like "
                    "<code style='background:rgba(var(--ds-accent-rgb),.15);padding:.1rem .35rem;"
                    "border-radius:4px;'>Quiz on 12 Oct, report due 20 Oct</code>."
                ),
                unsafe_allow_html=True,
            )

        # Welcome message (only show once)
        if len(st.session_state.messages) == 1:
            render_message(st.session_state.messages[0])

        # Display chat history
        for msg in st.session_state.messages[1:]:
            render_message(msg)

        # Chat input with image support
        user_input = st.chat_input(
            "Ask about deadlines or upload an image",
            accept_file=True,
            file_type=["jpg", "jpeg", "png"],
        )

        if user_input:
            parts = []
            if hasattr(user_input, 'text') and user_input.text:
                parts.append(types.Part.from_text(text=user_input.text))
                add_message("user", "text", user_input.text)
                render_message({"role": "user", "kind": "text", "content": user_input.text})
            elif hasattr(user_input, 'type'):
                bytes_data = user_input.getvalue()
                photo_part = types.Part.from_bytes(data=bytes_data, mime_type=user_input.type)
                parts.append(photo_part)
                parts.append(types.Part.from_text(
                    text="List every deadline and date you can find in this image."
                ))
                add_message("user", "image", bytes_data)
                render_message({"role": "user", "kind": "image", "content": bytes_data})
            else:
                parts.append(types.Part.from_text(text=str(user_input)))
                add_message("user", "text", str(user_input))
                render_message({"role": "user", "kind": "text", "content": str(user_input)})

            if parts:
                response = ask_gemini(parts)
                add_message("assistant", "text", response)
                render_message({"role": "assistant", "kind": "text", "content": response})
                extracted = extract_deadlines()
                if extracted:
                    st.session_state.deadlines = core.merge_deadlines(
                        st.session_state.deadlines, extracted
                    )
            st.rerun()

    # ── Deadlines tab ─────────────────────────────────────────────────────────
    with tab2:
        st.markdown(section_title_html("Your deadlines"))
        st.markdown(
            '<p style="font-size:.82rem;color:var(--ds-muted);margin:-.25rem 0 1rem;">'
            'Check the dates — AI can misread handwriting. Fix anything, then hit Email.</p>',
            unsafe_allow_html=True,
        )

        # Countdown cards for next 3 deadlines
        if deadlines:
            # Tag each deadline with its urgency for the countdown cards
            today = datetime.date.today()
            tagged = []
            for d in deadlines:
                d_copy = dict(d)
                d_copy["_urgency"] = core.urgency_label(d, today)
                tagged.append(d_copy)
            st.markdown(countdown_cards_html(tagged), unsafe_allow_html=True)
            st.markdown(divider_html(), unsafe_allow_html=True)

        # Urgency legend
        st.markdown(urgency_chips_html(), unsafe_allow_html=True)

        # Empty state
        if not deadlines:
            st.markdown(empty_deadlines_html("No deadlines yet — go to the Chat tab and upload a photo."), unsafe_allow_html=True)
        else:
            # Editable deadlines table
            for d in deadlines:
                d.setdefault("id", "")
                d.setdefault("title", "")
                d.setdefault("course", "")
                d.setdefault("date", "")
                d.setdefault("time", "")
                d.setdefault("type", "other")
                d.setdefault("est_hours", 1)
                d.setdefault("weight", 1)
                d.setdefault("confidence", "medium")
                d.setdefault("notes", "")
                d.setdefault("source", "typed")
            df = st.dataframe(
                deadlines,
                column_config={
                    "id": st.column_config.HiddenColumn(default=""),
                    "title": st.column_config.TextColumn("Title", default=""),
                    "course": st.column_config.TextColumn("Course", default=""),
                    "date": st.column_config.DateColumn("Date", default=""),
                    "time": st.column_config.TextColumn("Time", default=""),
                    "type": st.column_config.SelectboxColumn(
                        "Type",
                        options=["exam", "quiz", "assignment", "project", "lab", "event", "other"],
                        default="other",
                    ),
                    "est_hours": st.column_config.NumberColumn("Est. hours", default=1.0, min_value=0.1, step=0.5),
                    "weight": st.column_config.NumberColumn("Weight (1-5)", default=1, min_value=1, max_value=5, step=1),
                    "confidence": st.column_config.SelectboxColumn(
                        "Confidence",
                        options=["high", "medium", "low"],
                        default="medium",
                    ),
                    "notes": st.column_config.TextColumn("Notes", default=""),
                    "source": st.column_config.TextColumn("Source", default="typed", disabled=True),
                },
                use_container_width=True,
                hide_index=True,
            )
            # Sync edits back to session state
            if df is not None and df is not deadlines:
                st.session_state.deadlines = df.to_dict("records")

    # ── Workload tab ──────────────────────────────────────────────────────────
    with tab3:
        st.markdown(section_title_html("Study plan & workload"))
        st.markdown(
            '<p style="font-size:.82rem;color:var(--ds-muted);margin:-.25rem 0 1rem;">'
            'Start-by dates are calculated backwards from each due date.</p>',
            unsafe_allow_html=True,
        )

        if not deadlines:
            st.markdown(empty_workload_html(), unsafe_allow_html=True)
        else:
            today = datetime.date.today()
            sessions, unschedulable = core.build_study_plan(deadlines, daily_max_hours=4.0, today=today)
            crunch = core.find_crunch_days(deadlines)

            # Study plan table
            if sessions:
                st.markdown(
                    '<p style="font-size:.9rem;font-weight:600;color:var(--ds-text);margin:.5rem 0 .5rem;">'
                    'Suggested study sessions</p>',
                    unsafe_allow_html=True,
                )
                st.dataframe(
                    sessions,
                    column_config={
                        "date": st.column_config.DateColumn("Date"),
                        "title": st.column_config.TextColumn("Deadline"),
                        "hours": st.column_config.NumberColumn("Hours", format="%.1f"),
                    },
                    use_container_width=True,
                    hide_index=True,
                )

            # Crunch-day warnings
            if crunch:
                st.markdown(
                    '<p style="font-size:.9rem;font-weight:600;color:var(--ds-text);margin:.75rem 0 .5rem;">'
                    '⚠️ Crunch weeks detected</p>',
                    unsafe_allow_html=True,
                )
                for cw in crunch:
                    st.warning(
                        f"**Week {cw['year']}-W{cw['week']:02d}**: {cw['deadlines']} deadlines, "
                        f"~{cw['hours']}h of work. Sample: {', '.join(cw.get('sample_dates', [])[:2])}"
                    )

    # ── Header bar (top of main screen) ───────────────────────────────────────
    col1, col2 = st.columns([5, 2], vertical_alignment="center")
    with col1:
        st.markdown(
            f'<p style="font-size:.85rem;color:var(--ds-muted);margin:0;">'
            f'<strong style="color:var(--ds-text);">{PAGE_TITLE}</strong> {PAGE_ICON}</p>',
            unsafe_allow_html=True,
        )
    with col2:
        btn_disabled = st.session_state.get("sending", False)
        has_deadlines = bool(st.session_state.deadlines)
        if st.button("📧 Email my deadlines", type="primary", disabled=btn_disabled or not has_deadlines):
            st.session_state.sending = True
            st.rerun()
        if not has_deadlines:
            st.markdown(
                '<p style="font-size:.75rem;color:var(--ds-muted);margin-top:.25rem;text-align:right;">'
                'Add at least one deadline first</p>',
                unsafe_allow_html=True,
            )

    # ── Handle email sending ──────────────────────────────────────────────────
    if st.session_state.get("sending"):
        deadlines_send = st.session_state.deadlines
        if not deadlines_send:
            deadlines_send = extract_deadlines()
            if deadlines_send:
                st.session_state.deadlines = core.merge_deadlines(
                    st.session_state.deadlines, deadlines_send
                )
                deadlines_send = st.session_state.deadlines

        today = datetime.date.today()

        if not deadlines_send:
            st.info("I couldn't find any dated deadlines in this chat yet — try a clearer photo or type them in.")
            st.session_state.sending = False
            st.rerun()

        deadlines_send.sort(key=lambda d: d.get('date', '9999-12-31'))
        digest = build_digest(deadlines_send, today)
        ics_bytes = core.build_ics(deadlines_send)

        with st.expander("📧 Email preview"):
            st.markdown(
                f'<div style="font-size:.88rem;line-height:1.6;white-space:pre-wrap;">'
                f'{html_escape(digest)}</div>',
                unsafe_allow_html=True,
            )

        success, message = send_email(
            st.session_state.email,
            f"📅 Your {len(deadlines_send)} deadlines — DeadlineSnap",
            digest,
            ics_bytes,
        )

        if success:
            st.success(message)
        else:
            st.error(f"{message} — you can still download your files below.")
            st.info("You can still download the calendar file:")

        st.download_button(
            label="📅 Download Calendar (.ics)",
            data=ics_bytes,
            file_name="deadlines.ics",
            mime="text/calendar",
        )
        csv_data = core.to_csv(deadlines_send)
        st.download_button(
            label="📊 Download CSV",
            data=csv_data,
            file_name="deadlines.csv",
            mime="text/csv",
        )
        st.session_state.sending = False

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        # User chip
        initial = (st.session_state.name[0].upper() if st.session_state.name else "?")
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:.6rem;margin-bottom:1.25rem;">'
            f'<div style="width:36px;height:36px;border-radius:50%;'
            f'background:linear-gradient(135deg,var(--ds-accent),var(--ds-cyan));'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-weight:700;font-size:.9rem;color:#fff;flex-shrink:0;">'
            f'{initial}</div>'
            f'<div>'
            f'<div style="font-weight:600;font-size:.9rem;">{st.session_state.name}</div>'
            f'<div style="font-size:.75rem;color:var(--ds-muted);">{st.session_state.email}</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

        st.markdown(section_title_html("How it works"))
        st.write("1. Upload a photo of your syllabus/timetable")
        st.write("2. Type deadlines directly")
        st.write("3. Review and edit deadlines")
        st.write("4. Email yourself a digest + calendar file")

        st.markdown(divider_html(), unsafe_allow_html=True)
        st.info("💡 Tip: Use good lighting, capture the whole page, and ensure text is readable")
        st.markdown(divider_html(), unsafe_allow_html=True)

        st.markdown(
            '<p style="font-size:.75rem;color:var(--ds-muted);margin:0 0 .75rem;">'
            'Your data stays in this browser session — nothing is stored on our servers.</p>',
            unsafe_allow_html=True,
        )

        if st.button("🔄 Start over"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# ─── Entry point ──────────────────────────────────────────────────────────────

def main():
    """Main app function"""
    validate_secrets()
    init_session_state()

    if not st.session_state.onboarded:
        render_landing()
        st.stop()

    render_main()


if __name__ == "__main__":
    main()
