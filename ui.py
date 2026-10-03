"""DeadlineSnap UI — premium CSS/HTML skin, zero logic changes.

This module only contains ``inject_css()`` and pure HTML-string helpers.
It never touches st.session_state, Gemini, email, or any app logic.
Import and call inject_css() once after st.set_page_config in app.py.
"""

from html import escape as html_escape

# ─── Design tokens ────────────────────────────────────────────────────────────
# All spacing, colours, radii, typography and animation timing defined here
# so the rest of the stylesheet stays DRY and easy to adjust.
_TOKENS = """
<style>
/* ── CSS custom properties (design tokens) ───────────────────────────────── */
:root {
    --dsnap-accent:       #7C5CFF;
    --dsnap-accent-rgb:   124, 92, 255;
    --dsnap-cyan:         #22D3EE;
    --dsnap-cyan-rgb:     34, 211, 238;
    --dsnap-bg:           #0B1020;
    --dsnap-surface:      #121933;
    --dsnap-surface-hi:   rgba(255,255,255,.06);
    --dsnap-text:         #E8ECF8;
    --dsnap-text-muted:   rgba(232,236,248,.6);
    --dsnap-radius-sm:    8px;
    --dsnap-radius-md:    12px;
    --dsnap-radius-lg:    16px;
    --dsnap-radius-xl:    24px;
    --dsnap-font:         'Inter', system-ui, sans-serif;
    --dsnap-transition:   180ms cubic-bezier(.2,.8,.2,1);
    --dsnap-shadow-sm:    0 2px 8px rgba(0,0,0,.35);
    --dsnap-shadow-md:    0 4px 24px rgba(0,0,0,.4);
    --dsnap-shadow-glow:  0 0 20px rgba(var(--dsnap-accent-rgb),.25);
    --dsnap-hero-from:    #7C5CFF;
    --dsnap-hero-to:      #22D3EE;
    --dsnap-gap:          8px;
    --dsnap-type-display: 48px / 1.1;
    --dsnap-type-h2:      28px / 1.2;
    --dsnap-type-body:    16px / 1.6;
    --dsnap-type-caption: 13px / 1.5;
}

/* ── Inter font import ─────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Reset & base ───────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: var(--dsnap-font) !important;
    background: var(--dsnap-bg) !important;
    color: var(--dsnap-text) !important;
}

/* Streamlit chrome hiding */
#MainMenu          { visibility: hidden !important; }
header[data-testid="stHeader"] { display: none !important; }
footer              { visibility: hidden !important; }
[data-testid="stVerticalBlock"] > div:first-child { padding-top: .75rem !important; }

/* Selection colour */
::selection { background: rgba(var(--dsnap-accent-rgb), .35); color: #fff; }

/* Smooth scroll */
html { scroll-behavior: smooth; }

/* Slim themed scrollbar */
::-webkit-scrollbar            { width: 6px; height: 6px; }
::-webkit-scrollbar-track      { background: var(--dsnap-bg); }
::-webkit-scrollbar-thumb      { background: rgba(var(--dsnap-accent-rgb), .4); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover{ background: rgba(var(--dsnap-accent-rgb), .6); }
* { scrollbar-width: thin; scrollbar-color: rgba(var(--dsnap-accent-rgb),.4) var(--dsnap-bg); }

/* ── Prefers-reduced-motion ──────────────────────────────────────────────────── */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* ── Mobile ─────────────────────────────────────────────────────────────────── */
@media (max-width: 640px) {
    :root { --dsnap-type-display: 32px; --dsnap-type-h2: 22px; }
    .deadlinesnap-hero { padding: 1.25rem 1rem !important; }
    .deadlinesnap-glass { backdrop-filter: none !important; -webkit-backdrop-filter: none !important; }
    .aurora { display: none !important; }
    .st-chat-message { padding: .5rem !important; }
    button, .stButton > button, .deadlinesnap-pill { min-height: 44px !important; }
}

# KEYFRAME DEFINITIONS ───────────────────────────────────────────────────────
@keyframes dsnap-fade-up {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes dsnap-slide-in-right {
    from { opacity: 0; transform: translateX(12px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes dsnap-aurora {
    0%   { transform: translate(0, 0) scale(1); }
    33%  { transform: translate(30px, -20px) scale(1.05); }
    66%  { transform: translate(-20px, 15px) scale(.95); }
    100% { transform: translate(0, 0) scale(1); }
}
@keyframes dsnap-shimmer {
    0%   { transform: translateX(-100%); }
    100% { transform: translateX(200%); }
}
@keyframes dsnap-pulse-glow {
    0%, 100% { box-shadow: 0 0 4px rgba(var(--dsnap-accent-rgb),.3); }
    50%       { box-shadow: 0 0 14px rgba(var(--dsnap-accent-rgb),.6); }
}
@keyframes dsnap-spin-border {
    0%   { --angle: 0deg; }
    100% { --angle: 360deg; }
}

# PROPERTY DEFINITIONS (animated gradient border) ─────────────────────────────
@property --angle {
    syntax: '<angle>';
    initial-value: 0deg;
    inherits: false;
}

/* ════════════════════════════════════════════════════════════════════════════
   1. AMBIENT HERO BACKGROUND — aurora blobs + noise overlay
   ════════════════════════════════════════════════════════════════════════════ */
.deadlinesnap-hero-wrap {
    position: relative;
    border-radius: var(--dsnap-radius-lg);
    overflow: hidden;
    margin-bottom: 1.5rem;
}
.deadlinesnap-hero-wrap::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
        radial-gradient(ellipse 80% 60% at 20% 40%, rgba(var(--dsnap-accent-rgb), .35) 0%, transparent 60%),
        radial-gradient(ellipse 60% 80% at 80% 60%, rgba(var(--dsnap-cyan-rgb), .25) 0%, transparent 55%),
        radial-gradient(ellipse 50% 50% at 50% 50%, rgba(var(--dsnap-accent-rgb), .15) 0%, transparent 70%);
    filter: blur(40px);
    z-index: 0;
    pointer-events: none;
}
/* Animated blobs inside the hero */
.aurora {
    position: absolute;
    border-radius: 50%;
    filter: blur(60px);
    opacity: .5;
    pointer-events: none;
    z-index: 0;
}
.aurora--a { width: 320px; height: 320px; background: var(--dsnap-accent); top: -10%; left: 5%; animation: dsnap-aurora 20s ease-in-out infinite alternate; }
.aurora--b { width: 260px; height: 260px; background: var(--dsnap-cyan); bottom: -8%; right: 8%; animation: dsnap-aurora 16s ease-in-out infinite alternate-reverse; }
/* Subtle dot-grid overlay */
.deadlinesnap-hero-wrap::after {
    content: '';
    position: absolute;
    inset: 0;
    background-image: radial-gradient(rgba(255,255,255,.06) 1px, transparent 1px);
    background-size: 24px 24px;
    z-index: 1;
    pointer-events: none;
}
/* Hero content sits above everything */
.deadlinesnap-hero-content {
    position: relative;
    z-index: 2;
    text-align: center;
    padding: 2.5rem 2rem;
}
.deadlinesnap-hero-content h1 {
    font-size: var(--dsnap-type-display);
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin: 0 0 .4rem;
}
/* Gradient text on the key words */
.dsnap-gradient-text {
    background: linear-gradient(135deg, var(--dsnap-hero-from), var(--dsnap-hero-to));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.deadlinesnap-hero-content p {
    color: var(--dsnap-text-muted);
    font-size: 1.05rem;
    margin: 0;
    letter-spacing: .01em;
}

/* ════════════════════════════════════════════════════════════════════════════
   2. GLASSMORPHISM CARDS
   ════════════════════════════════════════════════════════════════════════════ */
.deadlinesnap-glass {
    background: rgba(18, 25, 51, .7);
    border: 1px solid rgba(var(--dsnap-accent-rgb), .2);
    border-radius: var(--dsnap-radius-lg);
    backdrop-filter: blur(12px) saturate(140%);
    -webkit-backdrop-filter: blur(12px) saturate(140%);
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,.06),
        var(--dsnap-shadow-md);
    /* Solid fallback when backdrop-filter is unsupported */
}
@supports not (backdrop-filter: blur(12px)) {
    .deadlinesnap-glass {
        background: var(--dsnap-surface);
        backdrop-filter: none;
        -webkit-backdrop-filter: none;
    }
}

/* Onboarding card with animated gradient border */
.deadlinesnap-card-wrap {
    position: relative;
    border-radius: var(--dsnap-radius-lg);
    padding: 2px;
    max-width: 480px;
    margin: 0 auto;
    /* Fallback: static border when @property is unsupported */
}
@supports not (background: conic-gradient(from var(--angle), red, blue)) {
    .deadlinesnap-card-wrap { border: 1px solid rgba(var(--dsnap-accent-rgb), .3); padding: 0; }
}
.deadlinesnap-card-wrap::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: inherit;
    padding: 2px;
    background: conic-gradient(from var(--angle), var(--dsnap-accent), var(--dsnap-cyan), var(--dsnap-accent));
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
    animation: dsnap-spin-border 4s linear infinite;
}
.deadlinesnap-card {
    background: var(--dsnap-surface);
    border-radius: calc(var(--dsnap-radius-lg) - 2px);
    padding: 2rem;
}

/* ════════════════════════════════════════════════════════════════════════════
   3. GRADIENT TEXT — handled above in hero h1 via .dsnap-gradient-text
   ════════════════════════════════════════════════════════════════════════════

   4. ANIMATED GRADIENT BORDER — handled in .deadlinesnap-card-wrap above
   ════════════════════════════════════════════════════════════════════════════

   5. STAGGERED ENTRANCE — fade-up on sections & cards
   ════════════════════════════════════════════════════════════════════════════ */
.dsnap-enter {
    animation: dsnap-fade-up .6s cubic-bezier(.2,.8,.2,1) both;
}
.dsnap-enter:nth-child(1)  { animation-delay: 0ms; }
.dsnap-enter:nth-child(2)  { animation-delay: 70ms; }
.dsnap-enter:nth-child(3)  { animation-delay: 140ms; }
.dsnap-enter:nth-child(4)  { animation-delay: 210ms; }
.dsnap-enter:nth-child(5)  { animation-delay: 280ms; }
.dsnap-enter:nth-child(6)  { animation-delay: 350ms; }

/* Chat messages animate in but don't re-trigger on rerun */
[data-testid="stChatMessage"] {
    animation: dsnap-slide-in-right .25s ease both;
}

/* ════════════════════════════════════════════════════════════════════════════
   6. BUTTONS
   ════════════════════════════════════════════════════════════════════════════ */
/* Primary */
button[kind="primary"],
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--dsnap-accent) 0%, #5B3FD4 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--dsnap-radius-md) !important;
    padding: .55rem 1.4rem !important;
    font-weight: 600 !important;
    font-size: .95rem !important;
    box-shadow: var(--dsnap-shadow-glow) !important;
    transition: transform var(--dsnap-transition), box-shadow var(--dsnap-transition) !important;
    position: relative;
    overflow: hidden;
}
button[kind="primary"]:hover,
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 24px rgba(var(--dsnap-accent-rgb), .45) !important;
}
button[kind="primary"]:active,
.stButton > button[kind="primary"]:active {
    transform: translateY(0) !important;
}
/* Shine sweep on hover */
button[kind="primary"]::after,
.stButton > button[kind="primary"]::after {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: linear-gradient(
        120deg,
        transparent 0%,
        rgba(255,255,255,.2) 40%,
        rgba(255,255,255,.35) 50%,
        transparent 60%,
        transparent 100%
    );
    transform: translateX(-100%);
    transition: none;
}
button[kind="primary"]:hover::after,
.stButton > button[kind="primary"]:hover::after {
    animation: dsnap-shimmer .7s ease forwards;
}
/* Visible focus ring */
button[kind="primary"]:focus-visible,
.stButton > button[kind="primary"]:focus-visible {
    outline: 2px solid var(--dsnap-cyan) !important;
    outline-offset: 2px !important;
}
/* Secondary / outlined buttons */
.stButton > button:not([kind]) {
    background: transparent !important;
    border: 1.5px solid rgba(var(--dsnap-accent-rgb), .5) !important;
    color: var(--dsnap-text) !important;
    border-radius: var(--dsnap-radius-md) !important;
    padding: .45rem 1.1rem !important;
    font-weight: 500 !important;
    transition: all var(--dsnap-transition) !important;
}
.stButton > button:not([kind]):hover {
    background: rgba(var(--dsnap-accent-rgb), .12) !important;
    border-color: var(--dsnap-accent) !important;
}
.stButton > button:not([kind]):focus-visible {
    outline: 2px solid var(--dsnap-cyan) !important;
    outline-offset: 2px !important;
}

/* ════════════════════════════════════════════════════════════════════════════
   7. CARD HOVER
   ════════════════════════════════════════════════════════════════════════════ */
.dsnap-hover-card {
    transition: transform var(--dsnap-transition), box-shadow var(--dsnap-transition), border-color var(--dsnap-transition) !important;
}
.dsnap-hover-card:hover {
    transform: translateY(-3px) !important;
    border-color: rgba(var(--dsnap-accent-rgb), .45) !important;
    box-shadow: var(--dsnap-shadow-md), 0 0 24px rgba(var(--dsnap-accent-rgb), .15) !important;
}

/* ════════════════════════════════════════════════════════════════════════════
   8. CHAT
   ════════════════════════════════════════════════════════════════════════════ */
[data-testid="stChatMessage"] {
    border-radius: var(--dsnap-radius-lg) !important;
    padding: .85rem 1.1rem !important;
    margin-bottom: .5rem !important;
}
/* Assistant bubbles on glass card */
[data-testid="stChatMessage"][data-testid="stChatMessageAssistant"] {
    background: rgba(var(--dsnap-accent-rgb), .08) !important;
    border: 1px solid rgba(var(--dsnap-accent-rgb), .15) !important;
    border-radius: var(--dsnap-radius-lg) !important;
}
/* User bubbles on accent gradient with white text */
[data-testid="stChatMessage"][data-testid="stChatMessageUser"] {
    background: linear-gradient(135deg, rgba(var(--dsnap-accent-rgb), .45), rgba(var(--dsnap-cyan-rgb), .3)) !important;
    border: 1px solid rgba(var(--dsnap-cyan-rgb), .3) !important;
    color: #fff !important;
}
/* Chat input */
[data-testid="stChatInput"] {
    border-radius: var(--dsnap-radius-lg) !important;
    border: 1.5px solid rgba(var(--dsnap-accent-rgb), .3) !important;
    background: var(--dsnap-bg) !important;
    transition: border-color var(--dsnap-transition), box-shadow var(--dsnap-transition) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--dsnap-accent) !important;
    box-shadow: 0 0 0 3px rgba(var(--dsnap-accent-rgb), .2) !important;
}

/* ════════════════════════════════════════════════════════════════════════════
   9. TABS — smooth sliding underline
   ════════════════════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    border-bottom: 2px solid rgba(var(--dsnap-accent-rgb), .15) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-radius: var(--dsnap-radius-sm) var(--dsnap-radius-sm) 0 0 !important;
    padding: .6rem 1.4rem !important;
    color: var(--dsnap-text-muted) !important;
    font-weight: 500 !important;
    font-size: .9rem !important;
    transition: color var(--dsnap-transition), background var(--dsnap-transition) !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--dsnap-text) !important;
    background: rgba(var(--dsnap-accent-rgb), .08) !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background: linear-gradient(90deg, var(--dsnap-accent), var(--dsnap-cyan)) !important;
    height: 3px !important;
    border-radius: 3px 3px 0 0 !important;
}
.stTabs [aria-selected="true"] {
    color: var(--dsnap-cyan) !important;
    font-weight: 600 !important;
    border-bottom: 2px solid var(--dsnap-cyan) !important;
    margin-bottom: -2px !important;
}

/* ════════════════════════════════════════════════════════════════════════════
   10. TRAFFIC-LIGHT CHIPS
   ════════════════════════════════════════════════════════════════════════════ */
.dsnap-chip {
    display: inline-flex;
    align-items: center;
    gap: .4rem;
    padding: .25rem .7rem;
    border-radius: 999px;
    font-size: .8rem;
    font-weight: 500;
    line-height: 1.4;
    white-space: nowrap;
}
.dsnap-chip::before {
    content: '';
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}
.dsnap-chip--overdue {
    background: rgba(255, 77, 77, .12);
    color: #ff6b6b;
    border: 1px solid rgba(255, 77, 77, .3);
}
.dsnap-chip--overdue::before { background: #ff4d4d; }
.dsnap-chip--overdue,
.dsnap-chip--due-soon {
    animation: dsnap-pulse-glow 2.4s ease-in-out infinite;
}
.dsnap-chip--due-soon {
    background: rgba(255, 174, 66, .12);
    color: #ffb84d;
    border: 1px solid rgba(255, 174, 66, .3);
}
.dsnap-chip--due-soon::before { background: #ffae42; }
.dsnap-chip--upcoming {
    background: rgba(255, 215, 0, .1);
    color: #ffd700;
    border: 1px solid rgba(255, 215, 0, .25);
}
.dsnap-chip--upcoming::before { background: #ffd700; }
.dsnap-chip--later {
    background: rgba(144, 238, 144, .1);
    color: #90ee90;
    border: 1px solid rgba(144, 238, 144, .25);
}
.dsnap-chip--later::before { background: #90ee90; }

/* ════════════════════════════════════════════════════════════════════════════
   11. LOADING / SPINNER
   ════════════════════════════════════════════════════════════════════════════ */
/* Spinner wrapper — accent-coloured animated indicator */
[data-testid="stSpinner"] > div {
    border-top-color: var(--dsnap-accent) !important;
}

/* Skeleton shimmer (for any placeholder blocks already present) */
.dsnap-skeleton {
    background: linear-gradient(90deg,
        var(--dsnap-surface) 25%,
        rgba(var(--dsnap-accent-rgb), .08) 50%,
        var(--dsnap-surface) 75%
    );
    background-size: 200% 100%;
    border-radius: var(--dsnap-radius-sm);
    animation: dsnap-shimmer 1.8s ease-in-out infinite;
}

/* ════════════════════════════════════════════════════════════════════════════
   12. SCROLLBAR, TOASTS, DATAFRAME, FILE UPLOADER, SIDEBAR
   ════════════════════════════════════════════════════════════════════════════ */
/* ── Toasts / Alerts (left accent bar) ─────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: var(--dsnap-radius-md) !important;
    border: none !important;
    border-left: 4px solid var(--dsnap-accent) !important;
    padding: .85rem 1.1rem !important;
    box-shadow: var(--dsnap-shadow-sm) !important;
}
[data-testid="stAlert"][role="alert"][class*="success"] { border-left-color: #22c55e !important; }
[data-testid="stAlert"][role="alert"][class*="warning"] { border-left-color: #f59e0b !important; }
[data-testid="stAlert"][role="alert"][class*="error"]   { border-left-color: #ef4444 !important; }
[data-testid="stAlert"][role="alert"][class*="info"]    { border-left-color: var(--dsnap-cyan) !important; }

/* ── Dataframe / Table ─────────────────────────────────────────────────────── */
.stDataFrame,
[data-testid="stDataFrame"] {
    border-radius: var(--dsnap-radius-md) !important;
    overflow: hidden !important;
    border: 1px solid rgba(var(--dsnap-accent-rgb), .15) !important;
}
.stDataFrame div[data-testid="stTable"],
[data-testid="stTable"] {
    background: var(--dsnap-surface) !important;
}
/* Header tint */
.stDataFrame header {
    background: rgba(var(--dsnap-accent-rgb), .12) !important;
    color: var(--dsnap-cyan) !important;
    font-weight: 600 !important;
}
/* Row hover */
.stDataFrame tbody tr:hover {
    background: rgba(var(--dsnap-accent-rgb), .08) !important;
}

/* ── Download button ───────────────────────────────────────────────────────── */
.stDownloadButton > button[kind="primary"] {
    background: linear-gradient(135deg, rgba(var(--dsnap-accent-rgb), .85), rgba(var(--dsnap-cyan-rgb), .7)) !important;
}

/* ── File uploader drop zone ───────────────────────────────────────────────── */
.stFileUploader > div {
    border: 2px dashed rgba(var(--dsnap-accent-rgb), .35) !important;
    border-radius: var(--dsnap-radius-lg) !important;
    background: rgba(var(--dsnap-accent-rgb), .04) !important;
    transition: border-color var(--dsnap-transition), box-shadow var(--dsnap-transition) !important;
}
.stFileUploader:hover > div {
    border-color: var(--dsnap-accent) !important;
    box-shadow: 0 0 16px rgba(var(--dsnap-accent-rgb), .2) !important;
}

/* ── Sidebar — glass panel + user chip ─────────────────────────────────────── */
/* Note: Streamlit sidebar class names are version-dependent. We target
   the container via data-testid where possible and use the known class
   as a fallback. */
[data-testid="stSidebar"] {
    background: rgba(var(--dsnap-accent-rgb), .04) !important;
    border-right: 1px solid rgba(var(--dsnap-accent-rgb), .15) !important;
    backdrop-filter: blur(8px) !important;
    -webkit-backdrop-filter: blur(8px) !important;
}
.css-1d391kg { /* legacy sidebar class, kept for compatibility */
    background: transparent !important;
    border-right: 1px solid rgba(var(--dsnap-accent-rgb), .15) !important;
    padding: 1rem !important;
}
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
.css-1d391kg h2, .css-1d391kg h3, .css-1d391kg h4 {
    color: var(--dsnap-cyan) !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
.css-1d391kg p, .css-1d391kg label, .css-1d391kg span {
    color: var(--dsnap-text) !important;
}

/* ── Form inputs ───────────────────────────────────────────────────────────── */
.stTextInput input,
.stNumberInput input,
.stSelectbox select,
.stTextArea textarea {
    border-radius: var(--dsnap-radius-md) !important;
    border: 1px solid rgba(var(--dsnap-accent-rgb), .3) !important;
    background: var(--dsnap-bg) !important;
    color: var(--dsnap-text) !important;
    transition: border-color var(--dsnap-transition), box-shadow var(--dsnap-transition) !important;
}
.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus,
.stSelectbox select:focus {
    border-color: var(--dsnap-accent) !important;
    box-shadow: 0 0 0 3px rgba(var(--dsnap-accent-rgb), .2) !important;
    outline: none !important;
}

/* ── Metrics ───────────────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--dsnap-surface) !important;
    border-left: 4px solid var(--dsnap-accent) !important;
    border-radius: var(--dsnap-radius-md) !important;
    padding: .85rem 1.1rem !important;
    box-shadow: var(--dsnap-shadow-sm) !important;
}
[data-testid="stMetricValue"] {
    font-variant-numeric: tabular-nums !important;
    font-weight: 700 !important;
}

/* ════════════════════════════════════════════════════════════════════════════
   13. DEPTH, DETAILS, DIVIDERS
   ════════════════════════════════════════════════════════════════════════════ */
/* Gradient divider between sections */
.dsnap-divider {
    height: 2px;
    margin: 1.5rem 0;
    background: linear-gradient(90deg, transparent, var(--dsnap-accent), var(--dsnap-cyan), transparent);
    border: none;
    border-radius: 2px;
}

/* Numeric tabular display */
.dsnap-tabular { font-variant-numeric: tabular-nums; }

/* ── Misc Streamlit elements ───────────────────────────────────────────────── */
.stExpander summary {
    color: var(--dsnap-text) !important;
    font-weight: 600 !important;
}
.stCheckbox label,
.stRadio label {
    color: var(--dsnap-text) !important;
}
</style>
"""


def inject_css() -> None:
    """Inject the DeadlineSnap custom CSS skin into the Streamlit page.

    Call this once immediately after ``st.set_page_config(...)`` in app.py.
    Pure CSS — no logic, no session-state, no Gemini, no email.
    """
    import streamlit as st
    st.markdown(_TOKENS, unsafe_allow_html=True)


def hero_html(title: str = "DeadlineSnap", tagline: str = "Snap your schedule. Never miss a deadline.") -> str:
    """Return pure HTML for the hero banner.

    Safe to call from app.py right after the header column block.
    All user-visible text is html.escape()d before insertion.
    """
    safe_title = html_escape(str(title))
    safe_tagline = html_escape(str(tagline))
    return (
        f'<div class="deadlinesnap-hero-wrap">'
        f'  <div class="aurora aurora--a"></div>'
        f'  <div class="aurora aurora--b"></div>'
        f'  <div class="deadlinesnap-hero-content">'
        f'    <h1><span class="dsnap-gradient-text">{safe_title}</span></h1>'
        f'    <p>{safe_tagline}</p>'
        f'  </div>'
        f'</div>'
    )


def chip_html(label: str, variant: str = "upcoming") -> str:
    """Return a traffic-light chip <span> for urgency legends or inline badges.

    *variant* must be one of: overdue, due-soon, upcoming, later.
    """
    safe_label = html_escape(str(label))
    valid = ("overdue", "due-soon", "upcoming", "later")
    cls = f"dsnap-chip dsnap-chip--{variant}" if variant in valid else "dsnap-chip dsnap-chip--upcoming"
    return f'<span class="{cls}">{safe_label}</span>'


def glass_card_html(inner_html: str, classes: str = "") -> str:
    """Wrap *inner_html* in a glassmorphism card container.

    The outer wrapper adds the animated gradient border; the inner div
    holds the actual translucent glass surface.
    """
    cls = f"deadlinesnap-card-wrap dsnap-hover-card {classes}".strip()
    return (
        f'<div class="{cls}">'
        f'  <div class="deadlinesnap-card">{inner_html}</div>'
        f'</div>'
    )
