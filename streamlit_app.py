"""Foster MBA Course Assistant — Streamlit front-end."""
from __future__ import annotations

import os
import streamlit as st

# ── ACCESS FLAG ───────────────────────────────────────────────────────────────
# Set to False when handing over to the program office for full deployment.
# That single change enables the complete RAG pipeline.
PUBLIC_DEMO_MODE = False

# Pull secrets into env vars (Streamlit Cloud uses st.secrets; local uses .env)
if not PUBLIC_DEMO_MODE:
    for _key in ["OPENAI_API_KEY", "OPENAI_CHAT_MODEL", "OPENAI_EMBEDDING_MODEL"]:
        if _key not in os.environ and _key in st.secrets:
            os.environ[_key] = st.secrets[_key]

    from openai import OpenAI  # noqa: E402
    from rag import answer_question, retrieve  # noqa: E402
    from relevance_agent import evaluate_relevance  # noqa: E402
    from schedule_agent import extract_codes_from_chunks, predict_offerings  # noqa: E402

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
    .stApp { font-family: 'Courier New', 'IBM Plex Mono', monospace; }

    /* ── Hero header: dark academic hall, brass-on-stone pillars ── */
    .hero {
        background: linear-gradient(135deg, #14091f 0%, #2b1246 55%, #38006B 100%);
        border-bottom: 1px solid rgba(241,182,134,0.25);
        border-radius: 0 0 18px 18px;
        padding: 0 0 28px 0;
        margin-bottom: 28px;
        text-align: center;
        overflow: hidden;
    }

    /* Four pillars, engraved brass */
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
        background: linear-gradient(90deg, #83502C, #F1B686);
        border-radius: 3px 3px 0 0;
    }
    .pillar-shaft {
        width: 22px;
        background: linear-gradient(to right, #6e4526, #C17E40, #F1B686, #C17E40, #6e4526);
        border-radius: 1px;
        opacity: 0.9;
    }
    .pillar-shaft.tall   { height: 80px; }
    .pillar-shaft.medium { height: 80px; }
    .pillar-shaft.short  { height: 80px; }
    .pillar-base {
        width: 34px; height: 6px;
        background: linear-gradient(90deg, #83502C, #F1B686);
        border-radius: 0 0 3px 3px;
    }
    .pillar-step {
        width: 100%;
        height: 6px;
        background: rgba(241,182,134,0.25);
        border-radius: 0 0 4px 4px;
    }

    /* Hero text — same shiny purple/bronze gradient as jensjungs.com */
    .hero-title {
        font-family: 'Courier New', monospace;
        font-size: 26px;
        font-weight: 700;
        letter-spacing: -0.01em;
        margin: 14px 0 4px;
        line-height: 1.2;
        background: linear-gradient(120deg, #E1BEE7, #C17E40 50%, #F1B686 100%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        filter: drop-shadow(0 0 12px rgba(193,126,64,0.3));
    }
    .hero-sub {
        color: rgba(232,227,240,0.6);
        font-size: 13px;
        margin: 0;
    }

    /* ── Chat messages ── */
    .user-msg {
        display: flex; justify-content: flex-end; margin: 6px 0;
    }
    .user-bubble {
        background: linear-gradient(135deg, #4A148C, #7B1FA2);
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
        background: linear-gradient(135deg, #83502C, #F1B686);
        color: #14091f;
        display: flex; align-items: center; justify-content: center;
        font-size: 12px; font-weight: 700; flex-shrink: 0; margin-top: 2px;
    }
    .ai-bubble {
        background: #150F22;
        border: 1px solid rgba(255,255,255,0.12);
        padding: 11px 16px;
        border-radius: 4px 18px 18px 18px;
        max-width: 82%;
        font-size: 15px;
        line-height: 1.65;
        word-break: break-word;
        color: #E8E3F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
        white-space: pre-wrap;
    }

    /* Schedule insight — brass plaque */
    .insight {
        background: rgba(193,126,64,0.1);
        border-left: 3px solid #C17E40;
        border-radius: 10px;
        padding: 10px 14px;
        font-size: 13px;
        line-height: 1.7;
        color: #E8DFC8;
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
        border: 1.5px solid rgba(156,77,204,0.5) !important;
        border-radius: 999px !important;
        background: #150F22 !important;
        color: #D8C4F0 !important;
        font-size: 13px !important;
        padding: 6px 16px !important;
        font-family: 'Courier New', monospace !important;
        transition: all .15s !important;
    }
    div[data-testid="column"] .stButton > button:hover {
        background: rgba(193,126,64,0.15) !important;
        border-color: #C17E40 !important;
        color: #F1B686 !important;
    }

    /* Input */
    .stChatInput > div { border-color: rgba(156,77,204,0.5) !important; border-radius: 24px !important; }
    .stChatInput > div:focus-within { border-color: #C17E40 !important; box-shadow: 0 0 0 3px rgba(193,126,64,.15) !important; }
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
    st.session_state.messages = []

if not PUBLIC_DEMO_MODE and "openai_client" not in st.session_state:
    st.session_state.openai_client = OpenAI()

ACCESS_DENIED = (
    "🎓 **This tool is exclusively available to enrolled UW Foster MBA students.**\n\n"
    "Due to intellectual property restrictions and the proprietary nature of the course "
    "materials used to power this assistant, public access to the full functionality is "
    "not permitted at this time.\n\n"
    "If you are a current Foster MBA student, please reach out to the program office "
    "to learn how to access this tool through official channels."
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

    if PUBLIC_DEMO_MODE:
        st.session_state.messages.append({"role": "user", "content": question})
        st.session_state.messages.append({"role": "assistant", "content": ACCESS_DENIED})
        st.rerun()

    else:
        client = st.session_state.openai_client
        history = st.session_state.messages[-8:]

        with st.spinner(""):
            relevance = evaluate_relevance(client, question, history)
            if not relevance["in_scope"]:
                reply = f"{relevance['reason']}\n\nTry: {relevance['suggested_rewrite']}"
                st.session_state.messages.append({"role": "user", "content": question})
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.rerun()

            retrieval_query = question
            if len(question.split()) < 8 and history:
                prior = " ".join(m["content"] for m in history[-2:] if m["role"] == "user")
                if prior:
                    retrieval_query = f"{prior} {question}"

            chunks = retrieve(client, retrieval_query)
            answer = answer_question(client, question, chunks, history)
            codes = extract_codes_from_chunks([(c.title, c.filename) for c in chunks])
            insight = predict_offerings(codes)

        st.session_state.messages.append({"role": "user", "content": question})
        st.session_state.messages.append({"role": "assistant", "content": answer, "insight": insight})
        st.rerun()
