# Simple_Chatbot.py
import streamlit as st
from streamlit.components.v1 import html
from dotenv import load_dotenv
from config import Config  # noqa: F401
from helpers.llm_helper import chat, stream_parser

load_dotenv()

# ── Page Setup: keep sidebar visible, mobile-friendly ────────────────────────────
st.set_page_config(
    page_title="Ask Coach Greg?",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",  # keep it open by default
)

# ── Responsive CSS: slim sidebar on mobile, tighter spacing, sticky input ───────
st.markdown(
    """
    <style>
      /* Desktop/tablet sidebar width */
      [data-testid="stSidebar"] {
        min-width: 280px;
        max-width: 280px;
      }
      /* Sidebar inner padding */
      [data-testid="stSidebar"] .block-container {
        padding-top: 0.75rem;
        padding-bottom: 1rem;
        padding-left: 0.75rem;
        padding-right: 0.75rem;
      }

      /* Main area: reasonable padding on small screens */
      @media (max-width: 640px) {
        .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }
        /* Make the sidebar narrower on phones */
        [data-testid="stSidebar"] {
          min-width: 220px !important;
          max-width: 220px !important;
        }
        /* Slightly smaller text only inside sidebar */
        [data-testid="stSidebar"] * {
          font-size: 0.95rem;
          line-height: 1.25rem;
        }
      }

      /* Avoid input zoom on iOS */
      textarea, input, .stTextInput, .stChatInputContainer textarea {
        font-size: 16px !important;
      }

      /* Keep images from overflowing */
      [data-testid="stImage"] img { max-width: 100% !important; height: auto !important; }

      /* Compact chat message spacing (can be toggled off) */
      .stChatMessage p { margin-bottom: 0.35rem !important; }

      /* Keep the chat input visible while scrolling on small screens */
      @media (max-width: 640px) {
        [data-testid="stChatInput"] { position: sticky; bottom: 0; z-index: 5; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Ensure the sidebar is open even on small viewports (Streamlit may collapse it) ─
html(
    """
    <script>
      const openSidebar = () => {
        const root = window.parent.document;
        const sidebar = root.querySelector('[data-testid="stSidebar"]');
        const btn = root.querySelector('[data-testid="collapsedControl"]');
        if (btn && sidebar && sidebar.getAttribute('aria-expanded') === 'false') {
          btn.click();  // expand if collapsed
        }
      };
      // Nudge once after load
      setTimeout(openSidebar, 150);
    </script>
    """,
    height=0,
)

# ── Header with quick Sidebar toggle button ──────────────────────────────────────
hc1, hc2 = st.columns([1, 0.28])
with hc1:
    st.title("Ask Coach Greg?")
with hc2:
    if st.button("☰ Sidebar", use_container_width=True):
        html(
            """
            <script>
              const btn = window.parent.document.querySelector('[data-testid="collapsedControl"]');
              if (btn) btn.click();
            </script>
            """,
            height=0,
        )

# ── Session State ────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# Keep history reasonable for performance on mobile
MAX_HISTORY = 50
if len(st.session_state.messages) > MAX_HISTORY:
    st.session_state.messages = st.session_state.messages[-MAX_HISTORY:]

# ── Sidebar Controls ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Coach Greg")

    # Headshot (png/jpg/jpeg)
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

    # Compact spacing toggle (sidebar-scoped)
    compact_mode = st.toggle("Compact mode (smaller spacing)", value=True, key="compact_sidebar")
    if not compact_mode:
        # Restore default paragraph spacing if user disables compact mode
        st.markdown(
            "<style>.stChatMessage p{margin-bottom:0.75rem!important}</style>",
            unsafe_allow_html=True,
        )

    # Reset chat
    if st.button("Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# ── Inline Quick Settings (useful on mobile without touching the sidebar) ────────
with st.expander("Quick Settings (mobile-friendly)"):
    st.write("**Model:** gpt-4o-mini")
    compact_inline = st.toggle("Compact mode (inline)", value=st.session_state.get("compact_sidebar", True), key="compact_inline")
    if compact_inline:
        st.markdown("<style>.stChatMessage p{margin-bottom:0.35rem!important}</style>", unsafe_allow_html=True)
    else:
        st.markdown("<style>.stChatMessage p{margin-bottom:0.75rem!important}</style>", unsafe_allow_html=True)

    if st.button("Reset Chat (inline)"):
        st.session_state.messages = []
        st.rerun()

# ── Internal Settings ────────────────────────────────────────────────────────────
temperature = 0.7
max_token_length = 1000

# ── Display Chat History ─────────────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Handle User Input ────────────────────────────────────────────────────────────
placeholder = "Ask about Agile or Traditional PM (e.g., ‘Sprint Review agenda’ or ‘baseline variance handling’)"
user_prompt = st.chat_input(placeholder)

if user_prompt:
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
                # Stream chunks for smooth UX
                stream_output = st.write_stream(stream_parser(llm_response))
            except Exception as e:
                stream_output = f"⚠️ Error generating response: {e}"
                st.error(stream_output)

    st.session_state.messages.append({"role": "assistant", "content": stream_output})

# ── Download Transcript (big tap target on mobile) ───────────────────────────────
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
