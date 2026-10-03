"""DeadlineSnap UI — pure CSS/HTML skin, zero logic changes.

This module only contains ``inject_css()`` and optional HTML string helpers.
It never touches st.session_state, Gemini, email, or any app logic.
Import and call inject_css() once after st.set_page_config in app.py.
"""

# Inter font via Google Fonts
_CSS = """
<style>
/* ── Reset & base ───────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* Hide Streamlit footer + reduce top padding */
#MainMenu { visibility: hidden; }
header[data-testid="stHeader"] { display: none; }
footer { visibility: hidden; }
[data-testid="stVerticalBlock"] > div:first-child { padding-top: 1rem !important; }

/* ── Hero banner ────────────────────────────────────────────── */
.deadlinesnap-hero {
    background: linear-gradient(135deg, #7C5CFF 0%, #22D3EE 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    text-align: center;
    box-shadow: 0 4px 24px rgba(124,92,255,.25);
}
.deadlinesnap-hero h1 {
    color: #ffffff !important;
    font-weight: 800 !important;
    font-size: 2.2rem !important;
    margin: 0 0 .25rem !important;
    letter-spacing: -.02em;
}
.deadlinesnap-hero p {
    color: rgba(255,255,255,.9) !important;
    font-size: 1rem !important;
    margin: 0 !important;
}

/* ── Card wrapper for onboarding ────────────────────────────── */
.deadlinesnap-card {
    background: #121933;
    border: 1px solid rgba(124,92,255,.25);
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 4px 32px rgba(0,0,0,.4);
    max-width: 480px;
    margin: 0 auto;
}

/* ── Gradient submit button ─────────────────────────────────── */
.deadlinesnap-btn-gradient {
    background: linear-gradient(135deg, #7C5CFF 0%, #22D3EE 100%) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 12px !important;
    padding: .6rem 1.5rem !important;
    width: 100%;
    transition: transform .15s ease, box-shadow .15s ease !important;
}
.deadlinesnap-btn-gradient:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(124,92,255,.4) !important;
}

/* ── Chat bubbles ───────────────────────────────────────────── */
.st-chat-message {
    border-radius: 16px !important;
    padding: .75rem 1rem !important;
}
[data-testid="stChatInput"] {
    border-radius: 16px !important;
}

/* ── Pill quick-action buttons ──────────────────────────────── */
.deadlinesnap-pill {
    display: inline-block;
    background: rgba(124,92,255,.15);
    border: 1px solid rgba(124,92,255,.4);
    color: #E8ECF8 !important;
    border-radius: 999px !important;
    padding: .35rem 1rem !important;
    font-size: .85rem !important;
    margin: .25rem .15rem !important;
    cursor: pointer;
    transition: background .15s ease !important;
}
.deadlinesnap-pill:hover {
    background: rgba(124,92,255,.3) !important;
}

/* ── Metric cards ───────────────────────────────────────────── */
.deadlinesnap-metric {
    background: #121933;
    border-left: 4px solid #7C5CFF;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    box-shadow: 0 2px 12px rgba(0,0,0,.3);
}

/* ── Tabs with active underline ─────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 2px solid rgba(124,92,255,.2) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-radius: 8px 8px 0 0 !important;
    padding: .5rem 1.25rem !important;
    color: #E8ECF8 !important;
    font-weight: 500 !important;
    transition: all .15s ease !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background: #7C5CFF !important;
    height: 3px !important;
    border-radius: 3px 3px 0 0 !important;
}
.stTabs [aria-selected="true"] {
    color: #22D3EE !important;
    border-bottom: 2px solid #22D3EE !important;
}

/* ── Primary / secondary buttons ────────────────────────────── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #7C5CFF 0%, #5B3FD4 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: .5rem 1.25rem !important;
    font-weight: 600 !important;
    transition: transform .15s ease, box-shadow .15s ease !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(124,92,255,.4) !important;
}
.stButton > button:not([kind]) {
    background: transparent !important;
    border: 1.5px solid rgba(124,92,255,.5) !important;
    color: #E8ECF8 !important;
    border-radius: 10px !important;
    padding: .45rem 1.1rem !important;
    font-weight: 500 !important;
    transition: all .15s ease !important;
}
.stButton > button:not([kind]):hover {
    background: rgba(124,92,255,.12) !important;
    border-color: #7C5CFF !important;
}

/* ── Sidebar ────────────────────────────────────────────────── */
.css-1d391kg { /* sidebar container */
    border-right: 1px solid rgba(124,92,255,.15) !important;
    padding: 1rem !important;
}
.css-1d391kg h2, .css-1d391kg h3, .css-1d391kg h4 {
    color: #22D3EE !important;
}
.css-1d391kg p, .css-1d391kg label, .css-1d391kg span {
    color: #E8ECF8 !important;
}

/* ── Form inputs ────────────────────────────────────────────── */
.stTextInput input, .stNumberInput input {
    border-radius: 10px !important;
    border: 1px solid rgba(124,92,255,.3) !important;
    background: #0B1020 !important;
    color: #E8ECF8 !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #7C5CFF !important;
    box-shadow: 0 0 0 2px rgba(124,92,255,.25) !important;
}

/* ── DataFrame / table ──────────────────────────────────────── */
.stDataFrame { border-radius: 12px !important; overflow: hidden; }
.stDataFrame div[data-testid="stTable"] { background: #121933 !important; }

/* ── Mobile-friendly tap targets ────────────────────────────── */
button, .stButton > button, a, .deadlinesnap-pill {
    min-height: 44px !important;
    min-width: 44px !important;
}

/* ── General contrast & readability ─────────────────────────── */
.stApp, .stMarkdown, .stText, p, span, label, div {
    color: #E8ECF8 !important;
}
.stCheckbox label, .stRadio label {
    color: #E8ECF8 !important;
}
</style>
"""


def inject_css() -> None:
    """Inject the DeadlineSnap custom CSS skin into the Streamlit page.

    Call this once immediately after ``st.set_page_config(...)`` in app.py.
    Pure CSS — no logic, no session-state, no Gemini, no email.
    """
    import streamlit as st
    st.markdown(_CSS, unsafe_allow_html=True)
