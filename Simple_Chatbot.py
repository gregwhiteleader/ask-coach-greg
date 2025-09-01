# Simple_Chatbot.py
import streamlit as st
from dotenv import load_dotenv
from helpers.llm_helper import chat, stream_parser
from config import Config  # noqa: F401

load_dotenv()

st.set_page_config(
    page_title="Ask Coach Greg?",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",  # no sidebar
)

# --- Minimal mobile-friendly CSS ---
st.markdown(
    """
    <style>
      .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }
      /* prevent iOS zoom on focus */
      textarea, input, .stTextInput, .stChatInputContainer textarea { font-size: 16px !important; }
      /* keep images from overflowing */
      [data-testid="stImage"] img { max-width: 100% !important; height: auto !important; }
      /* sticky chat input on small screens */
      @media (max-width: 640px) {
        [data-testid="stChatInput"] { position: sticky; bottom: 0; z-index: 5; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Header ---
left, right = st.columns([0.7, 0.3])
with left:
    st.title("Ask Coach Greg?")
    st.write("**Model:** gpt-4o-mini")  # static label on page
with right:
    if st.button("Reset Chat", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- Resolve bot avatar (your headshot) ---
bot_avatar = "🤖"
for fname in ("coach_greg.png", "coach_greg.jpg", "coach_greg.jpeg"):
    try:
        # just check existence by trying to display hidden (then not using the component)
        st.session_state["_avatar_probe"] = fname  # harmless store
        bot_avatar = fname
        break
    except Exception:
        continue

# --- Session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Limit history to keep mobile snappy
MAX_HISTORY = 50
if len(st.session_state.messages) > MAX_HISTORY:
    st.session_state.messages = st.session_state.messages[-MAX_HISTORY:]

# --- Render chat history ---
for message in st.session_state.messages:
    # Use your headshot for assistant messages, default for user
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
