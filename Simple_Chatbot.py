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

# --- Mobile-tuned CSS: smaller header on phones, circular avatar, sticky input ---
st.markdown(
    """
    <style>
      .block-container { padding-top: 0.75rem !important; padding-bottom: 1.25rem !important; }

      /* prevent iOS zoom on focus */
      textarea, input, .stTextInput, .stChatInputContainer textarea { font-size: 16px !important; }

      /* keep images from overflowing */
      [data-testid="stImage"] img { max-width: 100% !important; height: auto !important; }

      /* sticky chat input on small screens */
      @media (max-width: 640px) {
        [data-testid="stChatInput"] { position: sticky; bottom: 0; z-index: 5; }
      }

      /* header layout + sizing */
      .cg-avatar img {
        width: 72px !important; height: 72px !important;
        object-fit: cover !important; border-radius: 50% !important; display: block;
      }
      .cg-title h1 {
        margin-bottom: 0.25rem !important;
        line-height: 1.1 !important;
        /* responsive title: ~1.4rem on small, up to ~2.25rem on large */
        font-size: clamp(1.4rem, 4vw + 0.3rem, 2.25rem) !important;
      }
      .cg-subtle {
        margin-top: 0rem !important;
        color: #6b7280;
        font-size: clamp(0.9rem, 2.6vw, 1rem) !important;
      }

      /* On narrow screens, make header columns stack and shrink avatar/button */
      @media (max-width: 640px) {
        .cg-header-wrap .stColumn { width: 100% !important; display: block !important; }
        .cg-avatar img { width: 56px !important; height: 56px !important; }
        .cg-actions .stButton > button {
          width: 100% !important; padding: 0.45rem 0.75rem !important;
          font-size: 0.95rem !important;
        }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Utility: resolve avatar file if present ---
def resolve_avatar_path() -> str | None:
    for fname in ("coach_greg.png", "coach_greg.jpg", "coach_greg.jpeg"):
        if os.path.exists(fname):
            return fname
    return None

avatar_path = resolve_avatar_path()
bot_avatar = avatar_path if avatar_path else "🤖"

# --- Header: avatar + title/subtitle + action button (stacks on mobile) ---
st.markdown('<div class="cg-header-wrap">', unsafe_allow_html=True)
hcol_img, hcol_text, hcol_btn = st.columns([0.18, 0.62, 0.20])

with hcol_img:
    if avatar_path:
        st.markdown('<div class="cg-avatar">', unsafe_allow_html=True)
        st.image(avatar_path, width=72)  # CSS makes it circular & resizes on mobile
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("🤖")

with hcol_text:
    st.markdown('<div class="cg-title">', unsafe_allow_html=True)
    st.title("Ask Coach Greg?")
    st.markdown('<div class="cg-subtle"><strong>Model:</strong> gpt-4o-mini</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with hcol_btn:
    st.markdown('<div class="cg-actions">', unsafe_allow_html=True)
    if st.button("Reset", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- Session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Cap history for performance
MAX_HISTORY = 50
if len(st.session_state.messages) > MAX_HISTORY:
    st.session_state.messages = st.session_state.messages[-MAX_HISTORY:]

# --- Render chat history (assistant uses your headshot as avatar) ---
for message in st.session_state.messages:
    avatar = bot_avatar if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- Chat input & LLM call ---
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

# --- Download transcript ---
if st.session_state.messages:
    transcript = "\n\n".join(
        f"{m['role'].title()}: {m['content']}" for m in st.session_state.messages
    )
    st.download_button(
        "Download Chat Transcript",
        transcript,
        file_name="chat_transcript.txt",
        use_container_width=True,
    )
