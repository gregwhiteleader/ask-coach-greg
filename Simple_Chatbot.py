# Simple_Chatbot.py
import openai, logging
logging.warning(f"OpenAI version: {openai.__version__}, from: {openai.__file__}")

import streamlit as st
from dotenv import load_dotenv
from config import Config  # noqa: F401
from helpers.llm_helper import chat, stream_parser

load_dotenv()

# ---- Page Setup ----
st.set_page_config(
    page_title="Ask Coach Greg?",
    initial_sidebar_state="expanded",
)
st.title("Ask Coach Greg?")

# ---- Session State ----
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---- Sidebar Controls ----
with st.sidebar:
    # Headshot (png/jpg/jpeg)
    image_file = None
    for fname in ["coach_greg.png", "coach_greg.jpg", "coach_greg.jpeg"]:
        try:
            st.image(fname, width=150, caption="Coach Greg")
            image_file = fname
            break
        except Exception:
            continue
    if not image_file:
        st.warning("👆 Add 'coach_greg.png' or 'coach_greg.jpg' to show a picture here.")

    st.markdown("# Chat Options")

    # Model lock (cost-friendly)
    st.write("**Model:** gpt-4o-mini (locked)")
    model = "gpt-4o-mini"

    # Reset chat
    if st.button("Reset Chat"):
        st.session_state.messages = []
        if hasattr(st, "rerun"):
            st.rerun()
        else:
            st.experimental_rerun()

# ---- Internal Settings ----
temperature = 0.7
max_token_length = 1000

# ---- Display Chat History ----
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---- Handle User Input ----
placeholder = "Ask about Agile or Traditional PM (e.g., 'Sprint Review agenda' or 'baseline variance handling')"
if user_prompt := st.chat_input(placeholder):
    with st.chat_message("user"):
        st.markdown(user_prompt)

    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # Let the helper auto-detect: Agile-only, Traditional-only, or compare when ambiguous
    with st.spinner("Generating response..."):
        try:
            llm_response = chat(
                user_prompt,
                model=model,
                max_tokens=max_token_length,
                temp=temperature,
                use_openai=True,
                # NOTE: no force_compare flag passed, so auto-detect decides
            )
            stream_output = st.write_stream(stream_parser(llm_response))
        except Exception as e:
            stream_output = f"⚠️ Error generating response: {e}"
            st.error(stream_output)

    st.session_state.messages.append({"role": "assistant", "content": stream_output})

# ---- Download Transcript ----
if st.session_state.messages:
    transcript = "\n\n".join(
        f"{m['role'].title()}: {m['content']}" for m in st.session_state.messages
    )
    st.download_button(
        "Download Chat Transcript",
        transcript,
        file_name="chat_transcript.txt",
    )
