# Simple_Chatbot.py
import streamlit as st
from dotenv import load_dotenv
from config import Config  # noqa: F401
from helpers.llm_helper import chat, stream_parser

load_dotenv()

# ---- Page Setup (mobile-first) ----
st.set_page_config(
    page_title="Ask Coach Greg?",
    page_icon="🤖",
    layout="centered",                  # keeps a readable line length on phones
    initial_sidebar_state="collapsed",  # sidebar starts hidden on small screens
)

# ---- Minimal mobile CSS tweaks ----
st.markdown(
    """
    <style>
      /* Tighten vertical padding on small screens */
      @media (max-width: 640px) {
        .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }
        .stChatMessage { padding: 0.5rem 0.75rem !important; }
      }

      /* Keep images from overflowing */
      [data-testid="stImage"] img { max-width: 100% !important; height: auto !important; }

      /* Prevent mobile zoom on input focus by using >=16px font-size */
      textarea, input, .stTextInput, .stChatInputContainer textarea {
        font-size: 16px !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Ask Coach Greg?")

# ---- Session State ----
if "messages" not in st.session_state:
    st.session_state.messages = []

# (optional) keep history light for mobile performance
MAX_HISTORY = 50
if len(st.session_state.messages) > MAX_HISTORY:
    st.session_state.messages = st.session_state.messages[-MAX_HISTORY:]

# ---- Sidebar Controls ----
with st.sidebar:
    st.markdown("### Coach Greg")
    # Try multiple filenames; scale to sidebar width automatically
    image_file = None
    for fname in ["coach_greg.png", "coach_greg.jpg", "coach_greg.jpeg"]:
        try:
            st.image(fname, use_column_width=True, caption="Coach Greg")
            image_file = fname
            break
        except Exception:
            continue
    if not image_file:
        st.info("Add `coach_greg.png` (or .jpg/.jpeg) to show your headshot here.")

    st.divider()
    st.markdown("### Chat Options")
    st.write("**Model:** gpt-4o-mini (locked)")
    model = "gpt-4o-mini"

    compact = st.toggle("Compact mode (smaller spacing)", value=True)
    if compact:
        st.markdown(
            """
            <style>
              .stChatMessage p { margin-bottom: 0.25rem !important; }
            </style>
            """,
            unsafe_allow_html=True,
        )

    # Reset chat
    if st.button("Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# ---- Internal Settings ----
temperature = 0.7
max_token_length = 1000

# ---- Display Chat History ----
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Use markdown to keep copy readable on phones
        st.markdown(message["content"])

# ---- Handle User Input ----
placeholder = "Ask about Agile or Traditional PM (e.g., ‘Sprint Review agenda’ or ‘baseline variance handling’)"
user_prompt = st.chat_input(placeholder)

if user_prompt:
    # Render immediately for responsiveness
    with st.chat_message("user"):
        st.markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                llm_response = chat(
                    user_prompt,
                    model=model,
                    max_tokens=max_token_length,
                    temp=temperature,
                    use_openai=True,
                )
                # Stream chunks for a smoother feel on mobile
                stream_output = st.write_stream(stream_parser(llm_response))
            except Exception as e:
                stream_output = f"⚠️ Error generating response: {e}"
                st.error(stream_output)

    st.session_state.messages.append({"role": "assistant", "content": stream_output})

# ---- Download Transcript (put at end; large tap target on phones) ----
if st.session_state.messages:
    transcript = "\n\n".join(
        f"{m['role'].title()}: {m['content']}" for m in st.session_state.messages
    )
    st.download_button(
        "Download Chat Transcript",
        transcript,
        file_name="chat_transcript.txt",
        use_container_width=True,  # full-width button = easier tap on mobile
    )
