"""UI styling and rendering helpers for DeadlineSnap.

All CSS injection lives here so app.py stays logic-focused.
"""

import streamlit as st


# ---------------------------------------------------------------------------
# CSS injection
# ---------------------------------------------------------------------------

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Reset & base */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hide Streamlit default header/footer */
[data-testid="stHeader"] { display: none; }
[data-testid="stFooter"] { display: none; }

/* Tighten top padding */
.block-container { padding-top: 1.2rem; padding-bottom: 3rem; }

/* HERO banner */
.hero-banner {
    background: linear-gradient(135deg, #7C5CFF 0%, #22D3EE 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    color: #fff;
}
.hero-banner h1 {
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 0.3rem;
    color: #fff !important;
}
.hero-banner p {
    font-size: 1rem;
    opacity: 0.9;
    margin: 0 0 1rem;
}
.hero-pills { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.hero-pill {
    background: rgba(255,255,255,0.2);
    border: 1px solid rgba(255,255,255,0.35);
    border-radius: 20px;
    padding: 0.3rem 0.9rem;
    font-size: 0.8rem;
    color: #fff;
    backdrop-filter: blur(4px);
}

/* Onboarding card */
.onboard-card {
    background: #121933;
    border: 1px solid rgba(124,92,255,0.3);
    border-radius: 16px;
    padding: 2rem;
    max-width: 480px;
    margin: 2rem auto;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.privacy-note {
    font-size: 0.75rem;
    color: #8892b0;
    margin-top: 1rem;
    text-align: center;
}

/* Chat bubbles */
.chat-user {
    background: linear-gradient(135deg, #7C5CFF, #5b3fd4);
    color: #fff;
    border-radius: 16px 16px 4px 16px;
    padding: 0.75rem 1rem;
    max-width: 80%;
    margin-left: auto;
    margin-bottom: 0.5rem;
}
.chat-assistant {
    background: #121933;
    border: 1px solid rgba(124,92,255,0.25);
    border-radius: 16px 16px 16px 4px;
    padding: 0.75rem 1rem;
    max-width: 80%;
    margin-bottom: 0.5rem;
}

/* Quick-action chips */
.action-chips { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.75rem; }
.action-chip {
    background: #121933;
    border: 1px solid rgba(124,92,255,0.4);
    border-radius: 20px;
    padding: 0.35rem 0.85rem;
    font-size: 0.82rem;
    color: #E8ECF8;
    cursor: pointer;
    transition: background 0.15s;
}
.action-chip:hover { background: rgba(124,92,255,0.25); }

/* Metric cards */
.metric-card {
    background: #121933;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    border-left: 4px solid #7C5CFF;
    min-height: 80px;
}
.metric-card.overdue { border-left-color: #ff4d4d; }
.metric-card.warning  { border-left-color: #ffae42; }
.metric-card.caution  { border-left-color: #ffd700; }
.metric-card.safe     { border-left-color: #90ee90; }
.metric-card .label   { font-size: 0.75rem; color: #8892b0; text-transform: uppercase; letter-spacing: 0.05em; }
.metric-card .value   { font-size: 1.1rem; font-weight: 600; color: #E8ECF8; margin-top: 0.2rem; }
.metric-card .days    { font-size: 0.8rem; color: #8892b0; }

/* Urgency badge */
.badge {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 12px;
    font-size: 0.72rem;
    font-weight: 600;
}
.badge-overdue  { background: rgba(255,77,77,0.2); color: #ff6b6b; }
.badge-warning  { background: rgba(255,174,66,0.2); color: #ffbe42; }
.badge-caution  { background: rgba(255,215,0,0.2); color: #ffd700; }
.badge-safe     { background: rgba(144,238,144,0.2); color: #90ee90; }

/* Crunch alert */
.crunch-alert {
    background: rgba(255,77,77,0.1);
    border: 1px solid rgba(255,77,77,0.3);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.75rem;
    color: #ff6b6b;
    font-size: 0.88rem;
}

/* Sidebar user chip */
.user-chip {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    background: #121933;
    border: 1px solid rgba(124,92,255,0.25);
    border-radius: 12px;
    padding: 0.6rem 0.8rem;
    margin-bottom: 1rem;
}
.avatar {
    width: 36px; height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, #7C5CFF, #22D3EE);
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.9rem; color: #fff;
    flex-shrink: 0;
}
.user-info { font-size: 0.82rem; color: #E8ECF8; line-height: 1.3; }
.user-info .name { font-weight: 600; }
.user-info .email { color: #8892b0; font-size: 0.75rem; }

/* Stepper */
.step { display: flex; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.5rem; font-size: 0.85rem; color: #E8ECF8; }
.step-num {
    background: #7C5CFF;
    color: #fff;
    border-radius: 50%;
    width: 20px; height: 20px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.7rem; font-weight: 700; flex-shrink: 0;
}

/* Tip card */
.tip-card {
    background: rgba(34,211,238,0.08);
    border: 1px solid rgba(34,211,238,0.25);
    border-radius: 10px;
    padding: 0.6rem 0.8rem;
    font-size: 0.8rem;
    color: #90e0ef;
}

/* Buttons — cleaner look */
.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    min-height: 44px;
}

/* Tab styling */
[data-testid="stTabs"] { margin-top: 0.5rem; }
[data-testid="stTabs"] [data-testid="stTabContent"] { padding-top: 0.5rem; }

/* Data editor card */
.editor-card {
    background: #121933;
    border: 1px solid rgba(124,92,255,0.2);
    border-radius: 12px;
    padding: 1rem;
}

/* Action row */
.action-row { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.75rem; }

/* Responsive */
@media (max-width: 600px) {
    .hero-banner { padding: 1.25rem; }
    .hero-banner h1 { font-size: 1.4rem; }
    .onboard-card { margin: 1rem; padding: 1.25rem; }
    .metric-card { padding: 0.75rem; }
}
</style>
"""


def inject_css() -> None:
    """Inject custom CSS into the Streamlit page."""
    st.markdown(_CSS, unsafe_allow_html=True)


def render_hero() -> None:
    """Render the gradient hero banner."""
    st.markdown("""
<div class="hero-banner">
    <h1>DeadlineSnap</h1>
    <p>Snap your schedule. Never miss a deadline.</p>
    <div class="hero-pills">
        <span class="hero-pill">📸 Photo to deadlines</span>
        <span class="hero-pill">📋 Smart study plan</span>
        <span class="hero-pill">📅 Calendar & email</span>
    </div>
</div>
""", unsafe_allow_html=True)


def render_onboarding_card() -> None:
    """Render the onboarding form inside a styled card."""
    st.markdown('<div class="onboard-card">', unsafe_allow_html=True)
    yield  # placeholder — form rendered by caller
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="privacy-note">Your photos and emails are not stored. '
        'Everything lives in this session only.</p>',
        unsafe_allow_html=True,
    )


def render_quick_actions() -> None:
    """Render quick-action chip buttons."""
    st.markdown('<div class="action-chips">', unsafe_allow_html=True)
    for label in ["What's due this week?", "What should I start first?",
                   "Plan my week", "Any clashes?"]:
        st.markdown(
            f'<button class="action-chip" '
            f'onclick="Stroomlit.submit_form(\'quick_action\', \'{label}\')">{label}</button>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)


def render_metric_card(label: str, value: str, days: int, urgency: str) -> None:
    """Render a single countdown metric card."""
    cls = {
        "overdue": "overdue", "warning": "warning",
        "caution": "caution", "safe": "safe",
    }.get(urgency, "safe")
    st.markdown(f"""
<div class="metric-card {cls}">
    <div class="label">{label}</div>
    <div class="value">{value}</div>
    <div class="days">{days} days left</div>
</div>
""", unsafe_allow_html=True)


def render_urgency_badge(emoji: str, label: str) -> str:
    """Return an HTML badge string for urgency display."""
    cls_map = {
        "🔴": "badge-overdue", "🟠": "badge-warning",
        "🟡": "badge-caution", "🟢": "badge-safe",
    }
    cls = cls_map.get(emoji, "badge-safe")
    return f'<span class="badge {cls}">{emoji} {label}</span>'


def render_crunch_alert(message: str) -> None:
    """Render a crunch-week warning alert."""
    st.markdown(f'<div class="crunch-alert">⚠️ {message}</div>', unsafe_allow_html=True)


def render_user_chip(name: str, email: str) -> None:
    """Render the sidebar user chip."""
    initial = name[0].upper() if name else "?"
    st.markdown(f"""
<div class="user-chip">
    <div class="avatar">{initial}</div>
    <div class="user-info">
        <div class="name">{name}</div>
        <div class="email">{email}</div>
    </div>
</div>
""", unsafe_allow_html=True)


def render_stepper() -> None:
    """Render the 'How it works' numbered stepper."""
    steps = [
        "Upload a photo of your syllabus/timetable",
        "Type deadlines directly",
        "Review and edit deadlines",
        "Email yourself a digest + calendar file",
    ]
    for i, step in enumerate(steps, 1):
        st.markdown(f"""
<div class="step">
    <div class="step-num">{i}</div>
    <span>{step}</span>
</div>
""", unsafe_allow_html=True)


def render_tip_card() -> None:
    """Render the tip card."""
    st.markdown(
        '<div class="tip-card">💡 Use good lighting, capture the whole page, '
        'and ensure text is readable.</div>',
        unsafe_allow_html=True,
    )
