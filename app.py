"""DeadlineSnap - AI Vision Chatbot for Deadline Tracking"""

import datetime
import json
import smtplib
import uuid
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, Optional, List, Tuple

import streamlit as st
from google import genai
from google.genai import types

# Constants
MODEL_NAME = "gemini-3.5-flash"
PAGE_TITLE = "DeadlineSnap"
PAGE_ICON = "📅"

# Initialize page config
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")

# Cache Gemini client to avoid "client has been closed" bug
@st.cache_resource
def get_gemini_client() -> genai.Client:
    """Get cached Gemini client"""
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Secret validation
def validate_secrets() -> bool:
    """Check if all required secrets are present"""
    required_secrets = ["GEMINI_API_KEY", "GMAIL_ADDRESS", "GMAIL_APP_PASSWORD"]
    missing = [s for s in required_secrets if s not in st.secrets]
    if missing:
        st.error(f"Missing required secrets: {', '.join(missing)}")
        st.error("Please add these to your .streamlit/secrets.toml file")
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
            system_instruction = prompts.get_system_instruction(datetime.date.today())
            chat = client.chats.create(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(system_instruction=system_instruction)
            )

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
    """Ask Gemini with parts and return response"""
    try:
        with st.spinner("Thinking..."):
            response = st.session_state.chat.send_message(parts)
            return response.text
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}. Please try again."

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
    """Extract deadlines from conversation using hidden prompt"""
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
    """Send email with Gmail SMTP"""
    try:
        msg = MIMEMultipart()
        msg['From'] = st.secrets["GMAIL_ADDRESS"]
        msg['To'] = to_address
        msg['Subject'] = subject

        # Attach text body
        msg.attach(MIMEText(body, 'plain'))

        # Attach .ics file
        ics_part = MIMEBase('text', 'calendar')
        ics_part.set_payload(ics_bytes)
        ics_part.add_header('Content-Disposition', 'attachment', filename='deadlines.ics')
        msg.attach(ics_part)

        # Send
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(st.secrets["GMAIL_ADDRESS"], st.secrets["GMAIL_APP_PASSWORD"])
            server.send_message(msg)
        return True, "Email sent successfully"
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"

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
    validate_secrets()
    init_session_state()

    # Header
    col1, col2 = st.columns([5, 2], vertical_alignment="center")
    with col1:
        st.title(f"{PAGE_TITLE} {PAGE_ICON}")
    with col2:
        if len(st.session_state.messages) > 2:
            if st.button("📧 Email my deadlines", type="primary"):
                if not st.session_state.sending:
                    st.session_state.sending = True
                    st.rerun()

    # Sidebar
    with st.sidebar:
        st.caption(f"Logged in as: {st.session_state.name}")
        st.caption(f"Email: {st.session_state.email}")

        st.subheader("How it works")
        st.write("1. Upload a photo of your syllabus/timetable")
        st.write("2. Type deadlines directly")
        st.write("3. Review and edit deadlines")
        st.write("4. Email yourself a digest + calendar file")

        st.info("💡 Tip: Use good lighting, capture the whole page, and ensure text is readable")

        if st.button("🔄 Start Over"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # Onboarding or chat
    if not st.session_state.onboarded:
        st.info("Welcome to DeadlineSnap! Let's get you set up.")
        render_onboarding()
        st.stop()

    # Welcome message (only show once)
    if len(st.session_state.messages) == 1:
        render_message(st.session_state.messages[0])

    # Display chat history
    for msg in st.session_state.messages[1:]:
        render_message(msg)

    # Chat input
    user_input = st.chat_input("Ask about deadlines or upload an image", accept_file=True, file_type=["jpg", "jpeg", "png"])

    if user_input:
        # Add user message
        add_message("user", "text", user_input)
        render_message({"role": "user", "kind": "text", "content": user_input})

        # Prepare parts for Gemini
        parts = []

        # Add text
        parts.append(types.Part.from_text(text=user_input))

        # Process image if uploaded
        image_part = None
        if hasattr(st.session_state, '_uploaded_file'):
            image_part = process_image(st.session_state._uploaded_file)
            if image_part:
                parts.append(image_part)
                # Add the instruction for images
                parts.append(types.Part.from_text(text="List every deadline and date you can find in this image."))

        # Get response
        response = ask_gemini(parts)

        # Add response
        add_message("assistant", "text", response)
        render_message({"role": "assistant", "kind": "text", "content": response})

        # Extract deadlines if image was uploaded
        if image_part:
            extracted = extract_deadlines()
            if extracted:
                st.session_state.deadlines = core.merge_deadlines(st.session_state.deadlines, extracted)

        # Clear uploaded file
        if hasattr(st.session_state, '_uploaded_file'):
            del st.session_state._uploaded_file

        st.rerun()

    # Handle file upload
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"], key="file_uploader")
    if uploaded_file:
        st.session_state._uploaded_file = uploaded_file
        st.rerun()

# Handle email sending
if st.session_state.sending:
    deadlines = extract_deadlines()
    today = datetime.date.today()

    if not deadlines:
        st.info("I couldn't find any dated deadlines in this chat yet - try a clearer photo or type them in.")
        st.session_state.sending = False
        st.rerun()

    # Sort deadlines
    deadlines.sort(key=lambda d: d.get('date', '9999-12-31'))

    # Build digest
    digest = build_digest(deadlines, today)

    # Build .ics file
    ics_bytes = core.build_ics(deadlines)

    # Show preview
    with st.expander("📧 Email Preview"):
        st.write(digest)

    # Send email
    success, message = send_email(st.session_state.email, f"📅 Your {len(deadlines)} deadlines", digest, ics_bytes)

    if success:
        st.success(message)
    else:
        st.error(message)
        st.info("You can still download the calendar file:")
        st.download_button(
            label="📅 Download Calendar (.ics)",
            data=ics_bytes,
            file_name="deadlines.ics",
            mime="text/calendar"
        )

    st.session_state.sending = False

if __name__ == "__main__":
    import prompts
    import core
    main()