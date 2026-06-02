"""Foster MBA Course Assistant — Streamlit front-end (public demo)."""
from __future__ import annotations

import streamlit as st

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Foster MBA Course Assistant",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Hide Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 0 !important; max-width: 780px; }

    /* ── Hero header ── */
    .hero {
        background: linear-gradient(135deg, #4c1d95 0%, #7c3aed 60%, #a78bfa 100%);
        border-radius: 0 0 18px 18px;
        padding: 0 0 28px 0;
        margin-bottom: 28px;
        text-align: center;
        overflow: hidden;
    }

    /* Four pillars */
    .pillars-row {
        display: flex;
        justify-content: center;
        align-items: flex-end;
        gap: 18px;
        padding: 0 40px;
        margin-bottom: -2px;
    }
    .pillar-wrap { display: flex; flex-direction: column; align-items: center; }
    .pillar-cap {
        width: 38px; height: 8px;
        background: rgba(255,255,255,0.9);
        border-radius: 3px 3px 0 0;
    }
    .pillar-shaft {
        width: 22px;
        background: linear-gradient(to right, rgba(255,255,255,0.6), rgba(255,255,255,0.95), rgba(255,255,255,0.6));
        border-radius: 1px;
    }
    .pillar-shaft.tall   { height: 80px; }
    .pillar-shaft.medium { height: 80px; }
    .pillar-shaft.short  { height: 80px; }
    .pillar-base {
        width: 34px; height: 6px;
        background: rgba(255,255,255,0.85);
        border-radius: 0 0 3px 3px;
    }
    .pillar-step {
        width: 100%;
        height: 6px;
        background: rgba(255,255,255,0.4);
        border-radius: 0 0 4px 4px;
    }

    /* Hero text */
    .hero-title {
        color: #ffffff;
        font-size: 26px;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin: 14px 0 4px;
        line-height: 1.2;
    }
    .hero-sub {
        color: rgba(255,255,255,0.75);
        font-size: 13px;
        margin: 0;
    }

    /* ── Chat messages ── */
    .user-msg {
        display: flex; justify-content: flex-end; margin: 6px 0;
    }
    .user-bubble {
        background: #7c3aed;
        color: #fff;
        padding: 11px 16px;
        border-radius: 18px 4px 18px 18px;
        max-width: 75%;
        font-size: 15px;
        line-height: 1.55;
        word-break: break-word;
    }
    .ai-msg { display: flex; align-items: flex-start; gap: 10px; margin: 6px 0; }
    .ai-avatar {
        width: 30px; height: 30px; border-radius: 50%;
        background: #ede9fe; color: #7c3aed;
        display: flex; align-items: center; justify-content: center;
        font-size: 12px; font-weight: 700; flex-shrink: 0; margin-top: 2px;
    }
    .ai-bubble {
        background: #ffffff;
        border: 1px solid #e4e0f5;
        padding: 11px 16px;
        border-radius: 4px 18px 18px 18px;
        max-width: 82%;
        font-size: 15px;
        line-height: 1.65;
        word-break: break-word;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        white-space: pre-wrap;
    }

    /* Schedule insight */
    .insight {
        background: #ede9fe;
        border-left: 3px solid #7c3aed;
        border-radius: 10px;
        padding: 10px 14px;
        font-size: 13px;
        line-height: 1.7;
        color: #1a1a2e;
        margin-top: 8px;
        max-width: 82%;
        margin-left: 40px;
    }

    /* Suggestion chips */
    .chips-row {
        display: flex; flex-wrap: wrap; gap: 8px;
        justify-content: center; margin: 16px 0 4px;
    }

    /* Override Streamlit button style for chips */
    div[data-testid="column"] .stButton > button {
        border: 1.5px solid #c4b5fd !important;
        border-radius: 999px !important;
        background: #ffffff !important;
        color: #5b21b6 !important;
        font-size: 13px !important;
        padding: 6px 16px !important;
        transition: all .15s !important;
    }
    div[data-testid="column"] .stButton > button:hover {
        background: #ede9fe !important;
        border-color: #7c3aed !important;
    }

    /* Input */
    .stChatInput > div { border-color: #c4b5fd !important; border-radius: 24px !important; }
    .stChatInput > div:focus-within { border-color: #7c3aed !important; box-shadow: 0 0 0 3px rgba(124,58,237,.12) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero">
      <div class="pillars-row">
        <div class="pillar-wrap">
          <div class="pillar-cap"></div>
          <div class="pillar-shaft tall"></div>
          <div class="pillar-base"></div>
        </div>
        <div class="pillar-wrap">
          <div class="pillar-cap"></div>
          <div class="pillar-shaft medium"></div>
          <div class="pillar-base"></div>
        </div>
        <div class="pillar-wrap">
          <div class="pillar-cap"></div>
          <div class="pillar-shaft medium"></div>
          <div class="pillar-base"></div>
        </div>
        <div class="pillar-wrap">
          <div class="pillar-cap"></div>
          <div class="pillar-shaft tall"></div>
          <div class="pillar-base"></div>
        </div>
      </div>
      <div class="pillar-step"></div>
      <p class="hero-title">Foster MBA Course Assistant</p>
      <p class="hero-sub">UW Foster School of Business &nbsp;·&nbsp; Find your perfect elective</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []  # [{role, content}]

ACCESS_DENIED = (
    "🎓 **This tool is exclusively available to enrolled UW Foster MBA students.**\n\n"
    "Due to intellectual property restrictions and the proprietary nature of the course "
    "materials used to power this assistant, public access to the full functionality is "
    "not permitted at this time.\n\n"
    "If you are a current Foster MBA student, please reach out to the program office "
    "to learn how to access this tool through official channels.\n\n"
    "_Michael G. Foster School of Business — University of Washington, Seattle_"
)

# ── Suggestion chips (only on empty chat) ────────────────────────────────────
SUGGESTIONS = [
    "Which courses fit a corporate finance goal?",
    "I'm interested in startups — what should I take?",
    "What does MGMT 547 cover and when is it offered?",
    "Which courses cover sustainability or ESG?",
]

if not st.session_state.messages:
    st.markdown(
        "<p style='text-align:center;color:#6b6b8a;font-size:14px;margin-bottom:8px;'>"
        "Describe your goal or pick a question to get started:</p>",
        unsafe_allow_html=True,
    )
    cols = st.columns(2)
    for i, suggestion in enumerate(SUGGESTIONS):
        if cols[i % 2].button(suggestion, key=f"chip_{i}"):
            st.session_state.pending_input = suggestion
            st.rerun()

# ── Render chat history ───────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="user-msg"><div class="user-bubble">{msg["content"]}</div></div>',
            unsafe_allow_html=True,
        )
    else:
        text = msg["content"].replace("<", "&lt;").replace(">", "&gt;")
        insight_html = ""
        if msg.get("insight"):
            raw = msg["insight"].replace("<", "&lt;").replace(">", "&gt;")
            formatted = raw.replace("\n", "<br>").replace("**", "<strong>").replace("**", "</strong>")
            # Proper bold replacement
            import re
            formatted = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', msg["insight"])
            formatted = formatted.replace("\n", "<br>")
            insight_html = f'<div class="insight">{formatted}</div>'
        st.markdown(
            f'<div class="ai-msg"><div class="ai-avatar">AI</div>'
            f'<div class="ai-bubble">{text}</div></div>{insight_html}',
            unsafe_allow_html=True,
        )

# ── Handle chip pre-fill ──────────────────────────────────────────────────────
pending = st.session_state.pop("pending_input", None)

# ── Chat input ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask about Foster MBA courses…") or pending

if user_input:
    question = user_input.strip()

    st.markdown(
        f'<div class="user-msg"><div class="user-bubble">{question}</div></div>',
        unsafe_allow_html=True,
    )

    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.messages.append({"role": "assistant", "content": ACCESS_DENIED})
    st.rerun()
