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

st.markdown(
    """
    <style>
      .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }
      textarea, input, .stTextInput, .stChatInputContainer textarea { font-size: 16px !important; }
      [data-testid="stImage"] img { max-width: 100% !important; height: auto !important; }
      @media (max-width: 640px) {
        [data-testid="stChatInput"] { position: sticky; bottom: 0; z-index: 5; }
      }
      .cg-header img { border-radius: 9999px !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

def resolve_avatar_path() -> str | None:
    for fname in ("coach_greg.png", "coach_greg.jpg", "coach_greg.jpeg"):
        if os.path.exists(fname):
            return fname
    return None

avatar_path = resolve_avatar_path()
bot_avatar = avatar_path if avatar_path else "🤖"

hcol_img, hcol_text, hcol_btn = st.columns([0.16, 0.64, 0.20])
with hcol_img:
    if avatar_path:
        with st.container():
            st.markdown('<div class="cg-header">', unsafe_allow_html=True)
            st.image(avatar_path, use_column_width=True)  # <-- fixed here
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("🤖")

with hcol_text:
    st.title("Ask Coach Greg?")
    st.write("**Model:** gpt-4o-mini")

with hcol_btn:
    if st.button("Reset Chat", use_container_width=True):
        st.session_state.clear()
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

MAX_HISTORY = 50
if len(st.session_state.messages) > MAX_HISTORY:
    st.session_state.messages = st.session_state.messages[-MAX_HISTORY:]

for message in st.session_state.messages:
    avatar = bot_avatar if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

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
