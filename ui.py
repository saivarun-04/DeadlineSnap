"""DeadlineSnap UI — premium CSS/HTML skin, zero logic changes.

This module only contains ``inject_css()`` and pure HTML-string helpers.
It never touches st.session_state, Gemini, email, or any app logic.
Import and call inject_css() once after st.set_page_config in app.py.
"""

from html import escape as html_escape

# ════════════════════════════════════════════════════════════════════════════
# DESIGN TOKENS
# ════════════════════════════════════════════════════════════════════════════
_TOKENS = """<style>
/* ── CSS custom properties ─────────────────────────────────────────────────── */
:root {
    --ds-accent:      #7C5CFF;
    --ds-accent-rgb:  124, 92, 255;
    --ds-cyan:        #22D3EE;
    --ds-cyan-rgb:    34, 211, 238;
    --ds-bg:          #0B1020;
    --ds-surface:     #121933;
    --ds-text:        #E8ECF8;
    --ds-muted:       rgba(232,236,248,.6);
    --ds-radius-sm:   8px;
    --ds-radius-md:   12px;
    --ds-radius-lg:   16px;
    --ds-radius-xl:   24px;
    --ds-font:        'Inter', system-ui, sans-serif;
    --ds-tr:          180ms cubic-bezier(.2,.8,.2,1);
    --ds-shadow-sm:   0 2px 8px rgba(0,0,0,.35);
    --ds-shadow-md:   0 4px 24px rgba(0,0,0,.4);
    --ds-glow:        0 0 20px rgba(var(--ds-accent-rgb),.25);
    /* status colours — always paired with text labels */
    --ds-red:         #EF4444;
    --ds-orange:      #F59E0B;
    --ds-blue:        #3B82F6;
    --ds-green:       #22C55E;
}

/* ── Inter font import ─────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Reset & base ───────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: var(--ds-font) !important;
    background: var(--ds-bg) !important;
    color: var(--ds-text) !important;
}

#MainMenu          { visibility: hidden !important; }
header[data-testid="stHeader"] { display: none !important; }
footer              { visibility: hidden !important; }
[data-testid="stVerticalBlock"] > div:first-child { padding-top: .75rem !important; }
::selection         { background: rgba(var(--ds-accent-rgb), .35); color: #fff; }
html               { scroll-behavior: smooth; }

/* Slim themed scrollbar */
::-webkit-scrollbar            { width: 6px; height: 6px; }
::-webkit-scrollbar-track      { background: var(--ds-bg); }
::-webkit-scrollbar-thumb      { background: rgba(var(--ds-accent-rgb), .4); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover{ background: rgba(var(--ds-accent-rgb), .6); }
* { scrollbar-width: thin; scrollbar-color: rgba(var(--ds-accent-rgb),.4) var(--ds-bg); }

/* Fix for widget container height mismatch */
.st-emotion-cache-k2h9z6 {
    height: auto;
    min-height: min-content;
    align-items: stretch;
}
.st-emotion-cache-1edsnvj {
    display: block;
    min-height: 1.6em;
    overflow: visible;
}

/* Fix for widget container height mismatch */
.st-emotion-cache-k2h9z6 {
    height: auto;
    min-height: min-content;
    align-items: stretch;
}
.st-emotion-cache-1edsnvj {
    display: block;
    min-height: 1.6em;
    overflow: visible;
}

/* ── Reduced motion ─────────────────────────────────────────────────────────── */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* ── Mobile ─────────────────────────────────────────────────────────────────── */
@media (max-width: 640px) {
    :root { --ds-display: 32px; --ds-h2: 22px; }
    .ds-hero-wrap { padding: 1.25rem 1rem !important; }
    .ds-glass { backdrop-filter: none !important; -webkit-backdrop-filter: none !important; }
    .ds-aurora { display: none !important; }
    button, .stButton > button, .ds-pill { min-height: 44px !important; }
}

/* ── Keyframes ──────────────────────────────────────────────────────────────── */
@keyframes ds-fade-up {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes ds-slide-in {
    from { opacity: 0; transform: translateX(12px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes ds-aurora {
    0%   { transform: translate(0, 0) scale(1); }
    33%  { transform: translate(30px, -20px) scale(1.05); }
    66%  { transform: translate(-20px, 15px) scale(.95); }
    100% { transform: translate(0, 0) scale(1); }
}
@keyframes ds-shimmer {
    0%   { transform: translateX(-100%); }
    100% { transform: translateX(200%); }
}
@keyframes ds-pulse {
    0%, 100% { box-shadow: 0 0 4px rgba(var(--ds-accent-rgb),.3); }
    50%       { box-shadow: 0 0 14px rgba(var(--ds-accent-rgb),.6); }
}
@keyframes ds-spin {
    0%   { --ds-angle: 0deg; }
    100% { --ds-angle: 360deg; }
}

@property --ds-angle {
    syntax: '<angle>';
    initial-value: 0deg;
    inherits: false;
}

/* ════════════════════════════════════════════════════════════════════════════
   LANDING / HERO
   ════════════════════════════════════════════════════════════════════════════ */
.ds-hero-wrap {
    position: relative;
    border-radius: var(--ds-radius-lg);
    overflow: hidden;
    margin-bottom: 1.5rem;
    padding: 2.5rem 2rem;
    background: linear-gradient(135deg, rgba(var(--ds-accent-rgb),.18) 0%, rgba(var(--ds-cyan-rgb),.12) 100%);
}
.ds-hero-wrap::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
        radial-gradient(ellipse 80% 60% at 20% 40%, rgba(var(--ds-accent-rgb), .3) 0%, transparent 60%),
        radial-gradient(ellipse 60% 80% at 80% 60%, rgba(var(--ds-cyan-rgb), .2) 0%, transparent 55%);
    filter: blur(40px);
    z-index: 0;
    pointer-events: none;
}
.ds-aurora {
    position: absolute;
    border-radius: 50%;
    filter: blur(60px);
    opacity: .45;
    pointer-events: none;
    z-index: 0;
}
.ds-aurora--a { width: 300px; height: 300px; background: var(--ds-accent); top: -10%; left: 5%; animation: ds-aurora 20s ease-in-out infinite alternate; }
.ds-aurora--b { width: 240px; height: 240px; background: var(--ds-cyan); bottom: -8%; right: 8%; animation: ds-aurora 16s ease-in-out infinite alternate-reverse; }
.ds-hero-wrap::after {
    content: '';
    position: absolute;
    inset: 0;
    background-image: radial-gradient(rgba(255,255,255,.05) 1px, transparent 1px);
    background-size: 24px 24px;
    z-index: 1;
    pointer-events: none;
}
.ds-hero-content {
    position: relative;
    z-index: 2;
    text-align: center;
}
.ds-hero-content h1 {
    font-size: var(--ds-display, 48px);
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin: 1.25rem 0 .5rem;
    color: var(--ds-text);
}
.ds-hero-content p {
    font-size: 1.08rem;
    line-height: 1.55;
    color: var(--ds-text-muted);
    max-width: 620px;
    margin: 0 auto;
}
.ds-gradient-text {
    background: linear-gradient(135deg, var(--ds-accent), var(--ds-cyan));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.ds-hero-content p {
    color: var(--ds-muted);
    font-size: 1.05rem;
    margin: 0;
}
.ds-brand-chip {
    display: inline-flex;
    align-items: center;
    gap: .4rem;
    padding: .3rem .7rem;
    border-radius: 999px;
    background: rgba(var(--ds-accent-rgb), .15);
    border: 1px solid rgba(var(--ds-accent-rgb), .3);
    color: var(--ds-text);
    font-size: .82rem;
    font-weight: 600;
}

/* ── Step strip ─────────────────────────────────────────────────────────────── */
.ds-step-strip {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: .5rem;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
}
.ds-step {
    display: inline-flex;
    align-items: center;
    gap: .4rem;
    background: rgba(var(--ds-accent-rgb), .1);
    border: 1px solid rgba(var(--ds-accent-rgb), .25);
    border-radius: 999px;
    padding: .4rem .9rem;
    font-size: .85rem;
    font-weight: 500;
    color: var(--ds-text);
    white-space: nowrap;
}
.ds-step svg { flex-shrink: 0; }
.ds-step-arrow {
    color: var(--ds-muted);
    font-size: 1.1rem;
    user-select: none;
}

/* ── Feature cards ──────────────────────────────────────────────────────────── */
.ds-features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin: 1.5rem 0;
}
.ds-feature-card {
    background: rgba(var(--ds-accent-rgb), .06);
    border: 1px solid rgba(var(--ds-accent-rgb), .18);
    border-radius: var(--ds-radius-md);
    padding: 1rem 1.1rem;
    transition: transform var(--ds-tr), border-color var(--ds-tr), box-shadow var(--ds-tr);
}
.ds-feature-card:hover {
    transform: translateY(-3px);
    border-color: rgba(var(--ds-accent-rgb), .4);
    box-shadow: var(--ds-shadow-md), 0 0 20px rgba(var(--ds-accent-rgb), .12);
}
.ds-feature-card svg { margin-bottom: .5rem; }
.ds-feature-card h3 {
    font-size: .95rem;
    font-weight: 600;
    margin: 0 0 .25rem;
    color: var(--ds-text);
}
.ds-feature-card p {
    font-size: .8rem;
    color: var(--ds-muted);
    margin: 0;
    line-height: 1.5;
}

/* ── Onboarding form as glass card ──────────────────────────────────────────── */
/* Streamlit internal selector for the form container */
[data-testid="stForm"] {
    max-width: 520px !important;
    margin: 0 auto !important;
    padding: 28px 32px !important;
    border-radius: 24px !important;
    background: rgba(18, 25, 51, .85) !important;
    border: 1px solid rgba(var(--ds-accent-rgb), .25) !important;
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,.06),
        var(--ds-shadow-md) !important;
    position: relative;
}
/* Animated gradient border on the form */
[data-testid="stForm"]::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 24px;
    padding: 2px;
    background: conic-gradient(from var(--ds-angle), var(--ds-accent), var(--ds-cyan), var(--ds-accent));
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
    animation: ds-spin 4s linear infinite;
}
@supports not (background: conic-gradient(from var(--ds-angle), red, blue)) {
    [data-testid="stForm"] {
        border: 1px solid rgba(var(--ds-accent-rgb), .3) !important;
    }
    [data-testid="stForm"]::before { display: none; }
}

/* ── Staggered entrance ─────────────────────────────────────────────────────── */
.ds-enter {
    animation: ds-fade-up .6s cubic-bezier(.2,.8,.2,1) both;
}
.ds-enter:nth-child(1)  { animation-delay: 0ms; }
.ds-enter:nth-child(2)  { animation-delay: 70ms; }
.ds-enter:nth-child(3)  { animation-delay: 140ms; }
.ds-enter:nth-child(4)  { animation-delay: 210ms; }
.ds-enter:nth-child(5)  { animation-delay: 280ms; }
.ds-enter:nth-child(6)  { animation-delay: 350ms; }

/* ── Buttons ────────────────────────────────────────────────────────────────── */
button[kind="primary"],
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--ds-accent) 0%, #5B3FD4 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--ds-radius-md) !important;
    padding: .55rem 1.4rem !important;
    font-weight: 600 !important;
    font-size: .95rem !important;
    box-shadow: var(--ds-glow) !important;
    transition: transform var(--ds-tr), box-shadow var(--ds-tr) !important;
    position: relative;
    overflow: hidden;
    min-height: 44px !important;
}
button[kind="primary"]:hover,
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 24px rgba(var(--ds-accent-rgb), .45) !important;
}
button[kind="primary"]:active { transform: translateY(0) !important; }
button[kind="primary"]::after,
.stButton > button[kind="primary"]::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(
        120deg,
        transparent 0%,
        rgba(255,255,255,.2) 40%,
        rgba(255,255,255,.35) 50%,
        transparent 60%,
        transparent 100%
    );
    transform: translateX(-100%);
}
button[kind="primary"]:hover::after,
.stButton > button[kind="primary"]:hover::after {
    animation: ds-shimmer .7s ease forwards;
}
button[kind="primary"]:focus-visible,
.stButton > button[kind="primary"]:focus-visible {
    outline: 2px solid var(--ds-cyan) !important;
    outline-offset: 2px !important;
}
/* Outlined / secondary */
.stButton > button:not([kind]) {
    background: transparent !important;
    border: 1.5px solid rgba(var(--ds-accent-rgb), .5) !important;
    color: var(--ds-text) !important;
    border-radius: var(--ds-radius-md) !important;
    padding: .45rem 1.1rem !important;
    font-weight: 500 !important;
    min-height: 44px !important;
    transition: all var(--ds-tr) !important;
}
.stButton > button:not([kind]):hover {
    background: rgba(var(--ds-accent-rgb), .12) !important;
    border-color: var(--ds-accent) !important;
}
.stButton > button:not([kind]):focus-visible {
    outline: 2px solid var(--ds-cyan) !important;
    outline-offset: 2px !important;
}
/* Form submit button — full-width gradient */
[data-testid="stForm"] [type="submit"],
[data-testid="stFormSubmitButton"] button {
    width: 100% !important;
    height: 48px !important;
    background: linear-gradient(135deg, var(--ds-accent) 0%, var(--ds-cyan) 100%) !important;
    color: #fff !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    border: none !important;
    border-radius: var(--ds-radius-md) !important;
    box-shadow: var(--ds-glow) !important;
    transition: transform var(--ds-tr), box-shadow var(--ds-tr) !important;
}
[data-testid="stForm"] [type="submit"]:hover,
[data-testid="stFormSubmitButton"] button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 24px rgba(var(--ds-accent-rgb), .45) !important;
}
[data-testid="stForm"] [type="submit"]:active,
[data-testid="stFormSubmitButton"] button:active {
    transform: translateY(0) !important;
}
[data-testid="stForm"] [type="submit"]:focus-visible,
[data-testid="stFormSubmitButton"] button:focus-visible {
    outline: 2px solid var(--ds-cyan) !important;
    outline-offset: 2px !important;
}
/* Disabled button caption */
.stButton > button:disabled + span,
.stButton > button[disabled] + span {
    font-size: .78rem;
    color: var(--ds-muted);
}

/* ── Chat ───────────────────────────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
    border-radius: var(--ds-radius-lg) !important;
    padding: .85rem 1.1rem !important;
    margin-bottom: .5rem !important;
    animation: ds-slide-in .25s ease both;
}
[data-testid="stChatMessage"][data-testid="stChatMessageAssistant"] {
    background: rgba(var(--ds-accent-rgb), .08) !important;
    border: 1px solid rgba(var(--ds-accent-rgb), .15) !important;
}
[data-testid="stChatMessage"][data-testid="stChatMessageUser"] {
    background: linear-gradient(135deg, rgba(var(--ds-accent-rgb), .45), rgba(var(--ds-cyan-rgb), .3)) !important;
    border: 1px solid rgba(var(--ds-cyan-rgb), .3) !important;
    color: #fff !important;
}
[data-testid="stChatInput"] {
    border-radius: var(--ds-radius-lg) !important;
    border: 1.5px solid rgba(var(--ds-accent-rgb), .3) !important;
    background: var(--ds-bg) !important;
    transition: border-color var(--ds-tr), box-shadow var(--ds-tr) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--ds-accent) !important;
    box-shadow: 0 0 0 3px rgba(var(--ds-accent-rgb), .2) !important;
}

/* ── Tabs ───────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    border-bottom: 2px solid rgba(var(--ds-accent-rgb), .15) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-radius: var(--ds-radius-sm) var(--ds-radius-sm) 0 0 !important;
    padding: .6rem 1.4rem !important;
    color: var(--ds-muted) !important;
    font-weight: 500 !important;
    font-size: .9rem !important;
    transition: color var(--ds-tr), background var(--ds-tr) !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--ds-text) !important;
    background: rgba(var(--ds-accent-rgb), .08) !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background: linear-gradient(90deg, var(--ds-accent), var(--ds-cyan)) !important;
    height: 3px !important;
    border-radius: 3px 3px 0 0 !important;
}
.stTabs [aria-selected="true"] {
    color: var(--ds-cyan) !important;
    font-weight: 600 !important;
    border-bottom: 2px solid var(--ds-cyan) !important;
    margin-bottom: -2px !important;
}

/* ── Traffic-light chips ─────────────────────────────────────────────────────── */
.ds-chip {
    display: inline-flex;
    align-items: center;
    gap: .4rem;
    padding: .25rem .7rem;
    border-radius: 999px;
    font-size: .8rem;
    font-weight: 500;
    white-space: nowrap;
}
.ds-chip::before {
    content: '';
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}
.ds-chip--overdue {
    background: rgba(239,68,68,.12);
    color: #fca5a5;
    border: 1px solid rgba(239,68,68,.3);
}
.ds-chip--overdue::before { background: var(--ds-red); }
.ds-chip--due-soon {
    background: rgba(245,158,11,.12);
    color: #fcd34d;
    border: 1px solid rgba(245,158,11,.3);
}
.ds-chip--due-soon::before { background: var(--ds-orange); }
.ds-chip--in-progress {
    background: rgba(59,130,246,.12);
    color: #93c5fd;
    border: 1px solid rgba(59,130,246,.3);
}
.ds-chip--in-progress::before { background: var(--ds-blue); }
.ds-chip--upcoming {
    background: rgba(34,197,94,.12);
    color: #86efac;
    border: 1px solid rgba(34,197,94,.3);
}
.ds-chip--upcoming::before { background: var(--ds-green); }
.ds-chip--overdue,
.ds-chip--due-soon {
    animation: ds-pulse 2.4s ease-in-out infinite;
}

/* ── Pills (quick actions) ──────────────────────────────────────────────────── */
.ds-pill {
    display: inline-block;
    background: rgba(var(--ds-accent-rgb), .12);
    border: 1px solid rgba(var(--ds-accent-rgb), .35);
    border-radius: 999px;
    padding: .35rem 1rem;
    font-size: .82rem;
    color: var(--ds-text);
    margin: .2rem .15rem;
    cursor: pointer;
    min-height: 32px;
    transition: background var(--ds-tr), box-shadow var(--ds-tr);
}
.ds-pill:hover {
    background: rgba(var(--ds-accent-rgb), .25);
    box-shadow: 0 0 12px rgba(var(--ds-accent-rgb), .25);
}

/* ── Empty-state card ───────────────────────────────────────────────────────── */
.ds-empty {
    background: rgba(var(--ds-accent-rgb), .05);
    border: 1px dashed rgba(var(--ds-accent-rgb), .25);
    border-radius: var(--ds-radius-lg);
    padding: 2rem 1.5rem;
    text-align: center;
    color: var(--ds-muted);
}
.ds-empty h3 {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--ds-text);
    margin: 0 0 .5rem;
}
.ds-empty p {
    font-size: .88rem;
    margin: 0 0 1rem;
    line-height: 1.6;
}
.ds-empty ul {
    text-align: left;
    display: inline-block;
    padding-left: 1.2rem;
    margin: 0 0 1rem;
    font-size: .85rem;
    color: var(--ds-muted);
    line-height: 1.7;
}

/* ── Countdown card (top of deadlines tab) ──────────────────────────────────── */
.ds-countdown {
    background: var(--ds-surface);
    border-left: 4px solid var(--ds-accent);
    border-radius: var(--ds-radius-md);
    padding: .85rem 1.1rem;
    box-shadow: var(--ds-shadow-sm);
}
.ds-countdown--red    { border-left-color: var(--ds-red); }
.ds-countdown--orange { border-left-color: var(--ds-orange); }
.ds-countdown--blue   { border-left-color: var(--ds-blue); }
.ds-countdown--green  { border-left-color: var(--ds-green); }

/* ── Alerts / toasts ────────────────────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: var(--ds-radius-md) !important;
    border: none !important;
    border-left: 4px solid var(--ds-accent) !important;
    padding: .85rem 1.1rem !important;
    box-shadow: var(--ds-shadow-sm) !important;
}
[data-testid="stAlert"][role="alert"][class*="success"] { border-left-color: var(--ds-green) !important; }
[data-testid="stAlert"][role="alert"][class*="warning"] { border-left-color: var(--ds-orange) !important; }
[data-testid="stAlert"][role="alert"][class*="error"]   { border-left-color: var(--ds-red) !important; }
[data-testid="stAlert"][role="alert"][class*="info"]    { border-left-color: var(--ds-cyan) !important; }

/* ── Spinner ─────────────────────────────────────────────────────────────────── */
[data-testid="stSpinner"] > div { border-top-color: var(--ds-accent) !important; }

/* ── Dataframe ───────────────────────────────────────────────────────────────── */
.stDataFrame, [data-testid="stDataFrame"] {
    border-radius: var(--ds-radius-md) !important;
    overflow: hidden !important;
    border: 1px solid rgba(var(--ds-accent-rgb), .15) !important;
}
.stDataFrame div[data-testid="stTable"], [data-testid="stTable"] {
    background: var(--ds-surface) !important;
}
.stDataFrame header {
    background: rgba(var(--ds-accent-rgb), .12) !important;
    color: var(--ds-cyan) !important;
    font-weight: 600 !important;
}
.stDataFrame tbody tr:hover {
    background: rgba(var(--ds-accent-rgb), .08) !important;
}

/* ── File uploader ───────────────────────────────────────────────────────────── */
.stFileUploader > div {
    border: 2px dashed rgba(var(--ds-accent-rgb), .35) !important;
    border-radius: var(--ds-radius-lg) !important;
    background: rgba(var(--ds-accent-rgb), .04) !important;
    transition: border-color var(--ds-tr), box-shadow var(--ds-tr) !important;
}
.stFileUploader:hover > div {
    border-color: var(--ds-accent) !important;
    box-shadow: 0 0 16px rgba(var(--ds-accent-rgb), .2) !important;
}

/* ── Sidebar ─────────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: rgba(var(--ds-accent-rgb), .04) !important;
    border-right: 1px solid rgba(var(--ds-accent-rgb), .15) !important;
    backdrop-filter: blur(8px) !important;
    -webkit-backdrop-filter: blur(8px) !important;
}
.css-1d391kg { /* fallback for older Streamlit versions */
    border-right: 1px solid rgba(var(--ds-accent-rgb), .15) !important;
    padding: 1rem !important;
}
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
.css-1d391kg h2, .css-1d391kg h3, .css-1d391kg h4 {
    color: var(--ds-cyan) !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
.css-1d391kg p, .css-1d391kg label, .css-1d391kg span {
    color: var(--ds-text) !important;
}

/* ── Form inputs ─────────────────────────────────────────────────────────────── */
.stTextInput input,
.stNumberInput input,
.stSelectbox select,
.stTextArea textarea {
    border-radius: var(--ds-radius-md) !important;
    border: 1px solid rgba(var(--ds-accent-rgb), .3) !important;
    background: var(--ds-bg) !important;
    color: var(--ds-text) !important;
    transition: border-color var(--ds-tr), box-shadow var(--ds-tr) !important;
}
.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus,
.stSelectbox select:focus {
    border-color: var(--ds-accent) !important;
    box-shadow: 0 0 0 3px rgba(var(--ds-accent-rgb), .2) !important;
    outline: none !important;
}

/* ── Metrics ─────────────────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--ds-surface) !important;
    border-left: 4px solid var(--ds-accent) !important;
    border-radius: var(--ds-radius-md) !important;
    padding: .85rem 1.1rem !important;
    box-shadow: var(--ds-shadow-sm) !important;
}
[data-testid="stMetricValue"] {
    font-variant-numeric: tabular-nums !important;
    font-weight: 700 !important;
}

/* ── Misc ───────────────────────────────────────────────────────────────────── */
.stExpander summary {
    color: var(--ds-text) !important;
    font-weight: 600 !important;
}
.stCheckbox label, .stRadio label { color: var(--ds-text) !important; }

/* Gradient divider */
.ds-divider {
    height: 2px;
    margin: 1.5rem 0;
    background: linear-gradient(90deg, transparent, var(--ds-accent), var(--ds-cyan), transparent);
    border: none;
    border-radius: 2px;
}
.ds-tabular { font-variant-numeric: tabular-nums; }
.ds-section-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--ds-text);
    margin: 0 0 .75rem;
}
.ds-caption-muted {
    font-size: .78rem;
    color: var(--ds-muted);
    margin-top: .5rem;
}
.ds-trust-note {
    font-size: .75rem;
    color: var(--ds-muted);
    text-align: center;
    margin-top: 1rem;
    line-height: 1.5;
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


# ─── Pure HTML-string helpers ──────────────────────────────────────────────────
# Every helper accepts only static text or pre-escaped values.
# Dynamic user text MUST be passed via html.escape() before calling these helpers.


def _svg_icon(name: str) -> str:
    """Return an inline SVG string for a named icon (aria-hidden)."""
    icons: dict[str, str] = {
        "camera": (
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true">'
            '<path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>'
            '<circle cx="12" cy="13" r="4"/>'
            '</svg>'
        ),
        "edit": (
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true">'
            '<path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>'
            '<path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>'
            '</svg>'
        ),
        "calendar": (
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true">'
            '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>'
            '<line x1="16" y1="2" x2="16" y2="6"/>'
            '<line x1="8" y1="2" x2="8" y2="6"/>'
            '<line x1="3" y1="10" x2="21" y2="10"/>'
            '</svg>'
        ),
        "chart": (
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true">'
            '<line x1="18" y1="20" x2="18" y2="10"/>'
            '<line x1="12" y1="20" x2="12" y2="4"/>'
            '<line x1="6" y1="20" x2="6" y2="14"/>'
            '</svg>'
        ),
        "download": (
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true">'
            '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
            '<polyline points="7 10 12 15 17 10"/>'
            '<line x1="12" y1="15" x2="12" y2="3"/>'
            '</svg>'
        ),
        "phone": (
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true">'
            '<rect x="5" y="2" width="14" height="20" rx="2" ry="2"/>'
            '<line x1="12" y1="18" x2="12.01" y2="18"/>'
            '</svg>'
        ),
        "arrow": (
            '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true">'
            '<line x1="5" y1="12" x2="19" y2="12"/>'
            '<polyline points="12 5 19 12 12 19"/>'
            '</svg>'
        ),
        "check": (
            '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="2.5" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true">'
            '<polyline points="20 6 9 17 4 12"/>'
            '</svg>'
        ),
    }
    return icons.get(name, "")


def hero_html(title: str, tagline: str) -> str:
    """Pure HTML hero banner with brand chip, headline, and sub-paragraph."""
    safe_title = html_escape(str(title))
    return (
        f'<div class="ds-hero-wrap">'
        f'  <div class="ds-aurora ds-aurora--a"></div>'
        f'  <div class="ds-aurora ds-aurora--b"></div>'
        f'  <div class="ds-hero-content">'
        f'    <div class="ds-brand-chip">'
        f'      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" '
        f'        stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        f'        stroke-linejoin="round" aria-hidden="true">'
        f'        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>'
        f'        <line x1="16" y1="2" x2="16" y2="6"/>'
        f'        <line x1="8" y1="2" x2="8" y2="6"/>'
        f'        <line x1="3" y1="10" x2="21" y2="10"/>'
        f'      </svg>'
        f'      <span>{safe_title}</span>'
        f'    </div>'
        f'    <h1>Never miss a <span class="ds-gradient-text">submission</span> again.</h1>'
        f'    <p>Snap a photo of your timetable or syllabus. We pull out every deadline, '
        f'      build your study plan and send it to your calendar.</p>'
        f'  </div>'
        f'</div>'
    )


def step_strip_html() -> str:
    """3-step process strip with inline SVG icons."""
    steps = [
        ("camera", "Snap or type"),
        ("edit",   "Review and fix"),
        ("calendar", "Get it in your calendar"),
    ]
    parts = []
    for i, (icon_name, label) in enumerate(steps):
        if i > 0:
            parts.append('<span class="ds-step-arrow" aria-hidden="true">→</span>')
        parts.append(
            '<span class="ds-step">'
            + _svg_icon(icon_name)
            + '<span>' + label + '</span>'
            '</span>'
        )
    return '<div class="ds-step-strip">' + ''.join(parts) + '</div>'


def feature_cards_html() -> str:
    """Feature cards for the landing page."""
    features = [
        ("camera", "Photo to deadlines", "Upload a syllabus photo and get structured deadlines in seconds."),
        ("edit",   "Edit before it's sent", "Review and correct every date before anything leaves your device."),
        ("chart",  "Urgency at a glance", "Colour-coded chips show what's overdue, due soon, or up next."),
        ("calendar","Study plan builder", "Work backwards from due dates to schedule your study sessions."),
        ("download","Calendar + email export", "Download an .ics file or email yourself a full digest."),
        ("phone",  "Works on your phone", "Responsive design — use it on campus, at home, or on the go."),
    ]
    cards = []
    for icon_name, title, desc in features:
        cards.append(
            f'<div class="ds-feature-card ds-enter">'
            f'  {_svg_icon(icon_name)}'
            f'  <h3>{html_escape(title)}</h3>'
            f'  <p>{html_escape(desc)}</p>'
            f'</div>'
        )
    return '<div class="ds-features-grid">' + ''.join(cards) + '</div>'


def onboarding_card_html() -> str:
    """Wraps the onboarding form in a glass card with animated gradient border."""
    return (
        '<div class="ds-card-wrap ds-enter">'
        '  <div class="ds-card-inner">'
        '    <h2 style="margin:0 0 .25rem;font-size:1.3rem;font-weight:700;'
        '      color:var(--ds-text);text-align:center;">Get started — it\'s free</h2>'
        '    <p style="margin:0 0 1.25rem;font-size:.88rem;color:var(--ds-muted);'
        '      text-align:center;">No credit card. No sign-up wall. Just your deadlines.</p>'
        '  </div>'
        '</div>'
    )


def empty_chat_html(hint: str = "") -> str:
    """Empty-state card shown in the chat tab when no conversation has happened."""
    safe_hint = html_escape(str(hint))
    return (
        f'<div class="ds-empty ds-enter">'
        f'  <h3>No messages yet</h3>'
        f'  <p>{safe_hint}</p>'
        f'  <ul>'
        f'    <li>Take a clear photo of your timetable or syllabus</li>'
        f'    <li>Make sure the whole page is in frame and well-lit</li>'
        f'    <li>Ensure text is readable — blurry photos miss deadlines</li>'
        f'  </ul>'
        f'  <p style="font-size:.8rem;margin-top:.5rem;">'
        f'    Or type something like <code style="background:rgba(var(--ds-accent-rgb),.15);'
        f'    padding:.1rem .35rem;border-radius:4px;">Quiz on 12 Oct, report due 20 Oct</code>'
        f'  </p>'
        f'</div>'
    )


def empty_deadlines_html(return_hint: str = "") -> str:
    """Empty-state card for the deadlines tab when no data exists."""
    safe_hint = html_escape(str(return_hint))
    return (
        f'<div class="ds-empty ds-enter">'
        f'  <h3>No deadlines tracked yet</h3>'
        f'  <p>{safe_hint}</p>'
        f'  <span class="ds-pill">← Go to Chat and upload your timetable</span>'
        f'</div>'
    )


def empty_workload_html() -> str:
    """Empty-state card for the workload tab."""
    return (
        '<div class="ds-empty ds-enter">'
        '  <h3>No workload data yet</h3>'
        '  <p>Add some deadlines in the Chat or Deadlines tab first.<br/>'
        '     Study plans and crunch-day warnings appear here automatically.</p>'
        '</div>'
    )


def countdown_cards_html(deadlines: list) -> str:
    """Render up to 3 countdown cards for the top of the deadlines tab.

    Uses the existing core.urgency_label() return values:
      🔴 → overdue / red
      🟠 → due soon / orange
      🟡 → upcoming / yellow
      🟢 → later / green
    """
    if not deadlines:
        return ""
    colours = {"🔴": "red", "🟠": "orange", "🟡": "blue", "🟢": "green"}
    cards = []
    for d in deadlines[:3]:
        label, days = d.get("_urgency", ("⚪", 0))
        c = colours.get(label, "green")
        title = html_escape(str(d.get("title", "Untitled")))
        date = html_escape(str(d.get("date", "")))
        cards.append(
            f'<div class="ds-countdown ds-countdown--{c} ds-enter">'
            f'  <div class="ds-tabular" style="font-size:.8rem;color:var(--ds-muted);margin-bottom:.2rem;">'
            f'    {label} {days} day{"s" if abs(days) != 1 else ""}'
            f'  </div>'
            f'  <div style="font-weight:600;font-size:.95rem;">{title}</div>'
            f'  <div style="font-size:.8rem;color:var(--ds-muted);">{date}</div>'
            f'</div>'
        )
    return '<div class="ds-features-grid">' + ''.join(cards) + '</div>'


def urgency_chips_html() -> str:
    """Static legend row for traffic-light chips."""
    chips = [
        ("overdue",    "🔴 Overdue"),
        ("due-soon",   "🟠 Due soon"),
        ("in-progress","🟡 In progress"),
        ("upcoming",   "🟢 Upcoming"),
    ]
    parts = []
    for variant, label in chips:
        parts.append(f'<span class="ds-chip ds-chip--{variant}">{html_escape(label)}</span>')
    return '<div style="display:flex;gap:.5rem;flex-wrap:wrap;margin-bottom:1rem;">' + ''.join(parts) + '</div>'


def quick_action_pills_html() -> str:
    """Quick-action pill buttons for the chat tab."""
    actions = [
        ("What's due this week?", "📅"),
        ("What should I start first?", "🎯"),
        ("Plan my week", "📋"),
        ("Any clashes?", "⚠️"),
    ]
    parts = []
    for label, emoji in actions:
        parts.append(
            f'<span class="ds-pill" data-prompt="{html_escape(label)}">'
            f'{html_escape(emoji)} {html_escape(label)}</span>'
        )
    return '<div style="margin-bottom:.75rem;">' + ''.join(parts) + '</div>'


def divider_html() -> str:
    """Return a gradient divider using inline styles (avoids Streamlit markdown parsing issues)."""
    return (
        '<div style="height:2px;'
        'background:linear-gradient(90deg,transparent,rgba(124,92,255,.5),rgba(34,211,238,.5),transparent);'
        'margin:1.5rem 0;border-radius:2px;"></div>'
    )


def section_title_html(text: str) -> str:
    safe = html_escape(str(text))
    return f'<p class="ds-section-title">{safe}</p>'
