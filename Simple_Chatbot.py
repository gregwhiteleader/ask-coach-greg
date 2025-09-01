# Simple_Chatbot.py
import os
import streamlit as st
from dotenv import load_dotenv
from helpers.llm_helper import chat, stream_parser
from config import Config  # noqa: F401

load_dotenv()

st.set_page_config(
    page_title="Ask Coach Greg?",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------- CSS: small, circular header photo + tidy header + sticky input ----------
st.markdown("""
<style>
  .block-container { padding-top: 0.75rem !important; padding-bottom: 1.25rem !important; }

  /* prevent iOS zoom on focus */
  textarea, input, .stTextInput, .stChatInputContainer textarea { font-size: 16px !important; }

  /* sticky chat input on small screens */
  @media (max-width: 640px) {
    [data-testid="stChatInput"] { position: sticky; bottom: 0; z-index: 5; }
  }

  /* Title + subtitle sizing */
  .cg-title h1 {
    margin-bottom: 0.25rem !important;
    line-height: 1.1 !important;
    font-size: clamp(1.35rem, 4vw + 0.25rem, 2.15rem) !important;
  }
  .cg-subtle {
    margin-top: 0rem !important;
    color: #6b7280;
    font-size: clamp(0.9rem, 2.6vw, 1rem) !important;
  }

  /* ---- Header image rules (HIGH SPECIFICITY) ----
     Force a perfect circle, controlled size, and top-biased crop.
     Works regardless of how Streamlit wraps <img>.
  */
  .cg-header [data-testid="stImage"] img,
  .cg-header img {
    width: 72px !important;
    height: 72px !important;            /* keep square so border-radius makes a circle */
    border-radius: 50% !important;       /* circle */
    object-fit: cover !important;        /* crop to fill the circle */
    object-position: 50% 20% !important; /* bias upward so forehead isn't cut off */
    border: 2px solid #e5e7eb !important;
    display: block !important;
  }

  /* Stack header on phones + smaller avatar */
  @media (max-width: 640px) {
    .cg-header-wrap .stColumn { width: 100% !important; display: block !important; }
    .cg-header [data-testid="stImage"] img,
    .cg-header img {
      width: 56px !important;
      height: 56px !important;
    }
  }
</style>
""", unsafe_allow_html=True)

# ---------- Resolve avatar path (use your square if available) ----------
def find_avatar_path() -> str | None:
    for fname in (
        "coach_greg_square.png", "coach_greg_square.jpg",   # preferred (already square)
        "coach_greg.png", "coach_greg.jpg", "coach_greg.jpeg",
    ):
        if os.path.exists(fname):
            return fname
    return None

avatar_path = find_avatar_path()
bot_avatar = avatar_path if avatar_path else "🤖"

# ---------- Header: small circular photo + title/subtitle ----------
st.markdown('<div class="cg-header-wrap">', unsafe_allow_html=True)
hcol_img, hcol_text = st.columns([0.16, 0.84])

with hcol_img:
    if avatar_path:
        st.markdown('<div class="cg-header">', unsafe_allow_html=True)
        # width caps desktop size; CSS above enforces circle + mobile size override
        st.image(avatar_path, width=72)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("🤖")

with hcol_text:
    st.markdown('<div class="cg-title">', unsafe_allow_html=True)
    st.title("Ask Coach Greg?")
    st.markdown('<div class="cg-subtle"><strong>Model:</strong> gpt-4o-mini</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------- Session state ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Keep history performant on mobile
MAX_HISTORY = 50
if len(st.session_state.messages) > MAX_HISTORY:
    st.session_state.messages = st.session_state.messages[-MAX_HISTORY:]

# ---------- Render chat history (assistant uses your headshot as avatar) ----------
for message in st.session_state.messages:
    avatar = bot_avatar if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# ---------- Chat input & LLM call ----------
temperature = 0.7
max_token_length = 1000
placeholder = "Ask about Agile or Traditional PM (e.g., ‘Sprint Review agenda’ or ‘baseline variance handling’)"

if user_prompt := st.chat_input(placeholder):
    with st.chat_message("user"):
        st.markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    with st.chat_message("assistant", avatar=bot_avatar):
        with st.spinner("Thinking…"):
            try:
                llm_response = chat(
                    user_prompt,
                    model="gpt-4o-mini",
                    max_tokens=max_token_length,
                    temp=temperature,
                    use_openai=True,
                )
                stream_output = st.write_stream(stream_parser(llm_response))
            except Exception as e:
                stream_output = f"⚠️ Error generating response: {e}"
                st.error(stream_output)

    st.session_state.messages.append({"role": "assistant", "content": stream_output})

# ---------- Bottom actions (show after first turn) ----------
if st.session_state.messages:
    transcript = "\n\n".join(
        f"{m['role'].title()}: {m['content']}" for m in st.session_state.messages
    )
    col_dl, col_reset = st.columns(2)
    with col_dl:
        st.download_button(
            "Download Transcript",
            transcript,
            file_name="chat_transcript.txt",
            use_container_width=True,
        )
    with col_reset:
        if st.button("Reset Chat", use_container_width=True):
            st.session_state.clear()
            st.rerun()
